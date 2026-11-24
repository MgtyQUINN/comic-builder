"""Automatisk utsnitt: personene i fokus skal stå sentrert, med hele hodet i ruta.

Ansikter og personer finnes med Apple Vision (scripts/ansikter, bygges fra ansikter.swift ved behov)
og lagres i en buffer (JSON) så hvert bilde bare analyseres én gang.

  finn(stier, buffer)          -> {sti: {"b", "h", "ansikter", "personer"}}
  hodebokser(info)             -> (alle_hoder, hovedhode) som [x, y, b, h] i brøker, eller None
  utsnitt(iw, ih, bw, bh, zoom, info) -> (fx, fy, zoom)   fx/fy i % (CSS object-position)

Samme regel finnes i JS i bygg_serie.py (der rutestørrelsen først er kjent i nettleseren).
Regel: hodene til personene i fokus (ansikter minst 30 % så store som det største) sentreres vannrett,
litt over midten loddrett. Får de ikke plass, sentreres hovedpersonens hode; får heller ikke det plass
(smal rute, bredt bilde), sentreres selve ansiktet. Zoom senkes til det valgte får plass.
"""
import json
import os
import subprocess
from pathlib import Path

HER = Path(__file__).resolve().parent
BIN, SRC = HER / ".faces-bin", HER / "faces.swift"
MARG = 1.08       # luft rundt hodene
LODD = 0.45       # hodenes midtpunkt plasseres 45 % ned i ruta


def _bin():
    if not BIN.exists() or BIN.stat().st_mtime < SRC.stat().st_mtime:
        subprocess.run(["swiftc", "-O", str(SRC), "-o", str(BIN)], check=True, capture_output=True)
    return BIN


def finn(stier, buffer=None):
    stier = [str(Path(s).resolve()) for s in stier if s and Path(s).exists()]
    lager = {}
    if buffer and Path(buffer).exists():
        try:
            lager = json.loads(Path(buffer).read_text())
        except ValueError:
            lager = {}
    nokkel = {s: f"{s}|{os.path.getmtime(s):.0f}" for s in stier}
    mangler = sorted({s for s in stier if nokkel[s] not in lager})
    for i in range(0, len(mangler), 40):
        bit = mangler[i:i + 40]
        try:
            ut = subprocess.run([str(_bin())] + bit, capture_output=True, text=True, timeout=600).stdout
            svar = json.loads(ut or "{}")
        except (subprocess.SubprocessError, ValueError, OSError):
            svar = {}
        for s in bit:
            lager[nokkel[s]] = svar.get(s, {})
    if buffer and mangler:
        Path(buffer).write_text(json.dumps(lager))
    return {s: lager.get(nokkel[s], {}) for s in stier}


def _klipp(x, y, b, h):
    x0, y0 = max(0.0, x), max(0.0, y)
    x1, y1 = min(1.0, x + b), min(1.0, y + h)
    return [x0, y0, max(0.0, x1 - x0), max(0.0, y1 - y0)]


def _union(bokser):
    x0 = min(b[0] for b in bokser)
    y0 = min(b[1] for b in bokser)
    x1 = max(b[0] + b[2] for b in bokser)
    y1 = max(b[1] + b[3] for b in bokser)
    return [x0, y0, x1 - x0, y1 - y0]


def hodebokser(info):
    """Kandidater i prioritert rekkefølge: hodene til alle i fokus, hovedpersonens hode, hovedpersonens ansikt (stramt)."""
    if not info:
        return None
    ans = info.get("ansikter") or []
    hoder, stramt = [], None
    if ans:
        stor = max(a[2] * a[3] for a in ans)
        for (x, y, b, h) in sorted(ans, key=lambda a: -a[2] * a[3]):
            if b * h >= 0.3 * stor:
                hoder.append(_klipp(x - 0.3 * b, y - 0.7 * h, 1.6 * b, 2.0 * h))
                if stramt is None:
                    stramt = _klipp(x, y - 0.1 * h, b, 1.15 * h)
    else:
        pers = info.get("personer") or []
        if not pers:
            return None
        stor = max(p[2] * p[3] for p in pers)
        for (x, y, b, h) in sorted(pers, key=lambda p: -p[2] * p[3]):
            if b * h >= 0.3 * stor:
                hoder.append(_klipp(x + 0.25 * b, y, 0.5 * b, 0.22 * h))
    if not hoder:
        return None
    k = [_union(hoder), hoder[0]] + ([stramt] if stramt else [])
    return [[round(v, 4) for v in b] for b in k]


def utsnitt(iw, ih, bw, bh, zoom, info, fx=50.0, fy=50.0):
    """Beste object-position (fx, fy i %) og zoom for en rute på bw × bh (samme enhet begge)."""
    k = hodebokser(info)
    if not k or not iw or not ih or not bw or not bh:
        return fx, fy, zoom
    base = max(bw / iw, bh / ih)

    def vis(z):
        return bw / (iw * base * z), bh / (ih * base * z)

    vw, vh = vis(1.0)
    K = next((b for b in k if b[2] <= vw * 0.98 and b[3] <= vh * 0.98), k[-1])
    z = max(1.0, float(zoom))
    vw, vh = vis(z)
    if K[2] * MARG > vw or K[3] * MARG > vh:
        z = max(1.0, z * min(vw / (K[2] * MARG), vh / (K[3] * MARG)))
        vw, vh = vis(z)
    cx, cy = K[0] + K[2] / 2, K[1] + K[3] / 2
    L = min(max(cx - vw / 2, 0.0), max(1 - vw, 0.0))
    T = min(max(cy - vh * LODD, 0.0), max(1 - vh, 0.0))
    fx = L / (1 - vw) * 100 if vw < 0.9999 else 50.0
    fy = T / (1 - vh) * 100 if vh < 0.9999 else 50.0
    return round(fx, 2), round(fy, 2), round(z, 3)


JS = r"""
function utsnitt(){
 const kutt=[];
 document.querySelectorAll('img[data-k]').forEach(img=>{
  const c=img.parentElement, bw=c.clientWidth, bh=c.clientHeight; if(!bw||!bh) return;
  const iw=+img.dataset.iw, ih=+img.dataset.ih, ks=JSON.parse(img.dataset.k);
  const base=Math.max(bw/iw,bh/ih), vis=z=>[bw/(iw*base*z),bh/(ih*base*z)];
  let [vw,vh]=vis(1);
  const K=ks.find(b=>b[2]<=vw*0.98&&b[3]<=vh*0.98)||ks[ks.length-1];
  if(K[2]>vw*1.001||K[3]>vh*1.001){ const p=img.closest('[data-id]'); kutt.push(p?p.dataset.id:'?'); }
  let z=Math.max(1,+(img.dataset.z||1)); [vw,vh]=vis(z);
  if(K[2]*1.08>vw||K[3]*1.08>vh){ z=Math.max(1,z*Math.min(vw/(K[2]*1.08),vh/(K[3]*1.08))); [vw,vh]=vis(z); }
  const cx=K[0]+K[2]/2, cy=K[1]+K[3]/2;
  const L=Math.min(Math.max(cx-vw/2,0),Math.max(1-vw,0)), T=Math.min(Math.max(cy-vh*0.45,0),Math.max(1-vh,0));
  const fx=vw<0.9999?L/(1-vw)*100:50, fy=vh<0.9999?T/(1-vh)*100:50;
  img.style.objectPosition=fx.toFixed(2)+'% '+fy.toFixed(2)+'%';
  if(z>1.001){ Object.assign(img.style,{position:'absolute',width:(z*100).toFixed(2)+'%',height:(z*100).toFixed(2)+'%',
     left:(-(z-1)*fx).toFixed(2)+'%',top:(-(z-1)*fy).toFixed(2)+'%'}); }
  else { Object.assign(img.style,{position:'',width:'100%',height:'100%',left:'',top:''}); }
  img.dataset.utsnitt=fx.toFixed(1)+' '+fy.toFixed(1)+' z'+z.toFixed(2);
 });
 if(kutt.length) document.body.dataset.kutt=kutt.join(', ');
}
utsnitt();
"""


def kuttes(iw, ih, bw, bh, info):
    """True hvis ikke engang ansiktet til hovedpersonen får plass i ruta (bildet har feil format for ruta)."""
    k = hodebokser(info)
    if not k or not iw or not ih or not bw or not bh:
        return False
    base = max(bw / iw, bh / ih)
    vw, vh = bw / (iw * base), bh / (ih * base)
    return k[-1][2] > vw * 1.001 or k[-1][3] > vh * 1.001
