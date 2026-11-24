#!/usr/bin/env python3
"""Build a comic / graphic novel (PDF) from comic.json.

Usage:
  python3 build_comic.py <comic.json> [--variant NAME] [--format us|a4|a5|album]
                         [--bleed MM] [--grid] [--pages 1-4] [--png] [--plan] [--print-style NAME]

Writes <Title>[ - variant].html and .pdf next to comic.json.
  --plan         list every panel's size on the page and the best image aspect ratio; builds nothing
  --grid         draw a 10 % grid in every panel (for placing balloons)
  --pages        build only some pages (e.g. 3 or 2-5); include 0 to get the cover
  --png          also write a PNG of every page to <folder>/pages-png[ - variant]/
  --bleed        bleed in mm (3 for print). Images then run to the trim edge on splash pages and the cover
  --print-style  override print_style: none, bw-ink, bw-screentone, greyscale, four-color

Panels without an image are drawn as grey placeholders with the panel id and the start of the
prompt, so the whole comic can be read as a sketch before any image exists.
Needs python3 and Google Chrome (or Chromium/Edge). All lettering is real text, never part of the image.
comic.json may use English field names (see comic_aliases.py) or the original Norwegian ones.
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HER = Path(__file__).resolve().parent
FONTER = HER.parent / "fonts"
sys.path.insert(0, str(HER))
import layouts as oppsett_mod  # noqa: E402  ferdige sideoppsett (diagonal, innfelt, oppslag …)
import focus as fokus_mod  # automatic framing: keep the people in focus centred
import comic_aliases  # English field names → internal names

CHROME_KANDIDATER = [
    os.environ.get("CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    shutil.which("google-chrome") or "", shutil.which("google-chrome-stable") or "",
    shutil.which("chromium") or "", shutil.which("chromium-browser") or "", shutil.which("msedge") or "",
]

# bredde, høyde, marg (mm), mellomrom mellom paneler (mm), skrift i bobler (pt)
FORMATER = {
    "us":    (168.3, 260.4, 11, 3.0, 8.0),   # amerikansk comic / graphic novel (6.625 × 10.25 in)
    "a5":    (148.0, 210.0, 9, 2.6, 7.2),    # liten graphic novel / manga-størrelse
    "a4":    (210.0, 297.0, 12, 3.5, 9.5),
    "album": (240.0, 320.0, 13, 4.0, 10.5),  # fransk-belgisk album
}
JPG_KVALITET = 88
VENV_PY = next((p for p in (HER.parent / ".venv/bin/python", HER.parent / ".venv/Scripts/python.exe") if p.exists()),
               HER.parent / ".venv/bin/python")
STIL = {"navn": None, "raster_mm": 0.55, "maal": {}}  # settes i main()
STILER = ("sorthvitt", "sorthvitt-raster", "firefarge", "gratone")
MAKS_PX = 0  # settes i main(): 0 = full oppløsning (trykk), ellers største side i px for lese-PDF
FLOW_FORMATER = {"16:9": 16 / 9, "4:3": 4 / 3, "1:1": 1.0, "3:4": 3 / 4, "9:16": 9 / 16}


def esc(t):
    return html.escape(t or "")


def tekst_html(t):
    """*ord* → uthevet, linjeskift beholdes."""
    t = esc(t)
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    return t.replace("\n", "<br>")


def bilde_url(mappe: Path, sti: str):
    if not sti:
        return None
    p = (mappe / os.path.expanduser(sti)).resolve()
    if not p.exists():
        print(f"WARNING: missing image {p}", file=sys.stderr)
        return None
    if MAKS_PX or p.suffix.lower() in (".webp", ".png"):
        # Lese-PDF: nedskalert JPG-kopi (PDF-en blir ellers svær, særlig når samme bilde brukes i flere paneler).
        # WebP/PNG gjøres alltid om til JPG. Originalen røres ikke.
        import hashlib
        cache = mappe / ".jpg-til-pdf"
        cache.mkdir(exist_ok=True)
        nokkel = hashlib.md5(f"{p}|{MAKS_PX}".encode()).hexdigest()[:10]
        j = cache / f"{p.stem}-{nokkel}.jpg"
        if not j.exists() or j.stat().st_mtime < p.stat().st_mtime:
            til_jpg(p, j, JPG_KVALITET if not MAKS_PX else 82, MAKS_PX)
        return j.as_uri()
    return p.as_uri()


def til_jpg(inn, ut, kvalitet, maks_px):
    """Convert/downscale an image to JPG: sips on macOS, otherwise Pillow (in the skill's .venv)."""
    if shutil.which("sips"):
        kmd = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(kvalitet)]
        if maks_px:
            kmd += ["-Z", str(maks_px)]
        subprocess.run(kmd + [str(inn), "--out", str(ut)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    kode = ("import sys;from PIL import Image;im=Image.open(sys.argv[1]).convert('RGB');m=int(sys.argv[4])\n"
            "if m: im.thumbnail((m,m))\nim.save(sys.argv[2],quality=int(sys.argv[3]))")
    py = str(VENV_PY) if VENV_PY.exists() else sys.executable
    subprocess.run([py, "-c", kode, str(inn), str(ut), str(kvalitet), str(maks_px or 0)], check=True)


def stil_url(mappe, p, zoom):
    """Kjør stilfilteret (sorthvitt/firefarge) på panelbildet, med rasterprikker i fast størrelse på siden."""
    navn = p.get("stilfilter", STIL["navn"])
    if not navn or navn == "ingen" or not p.get("bilde"):
        return None
    if navn not in STILER:
        print(f"WARNING: unknown print_style {navn}", file=sys.stderr)
        return None
    kilde = (mappe / os.path.expanduser(p["bilde"])).resolve()
    maal = STIL["maal"].get(id(p))
    if not kilde.exists() or not maal:
        return None
    if not VENV_PY.exists():
        sys.exit(f"The print style needs {VENV_PY} – in the skill folder run: python3 -m venv .venv && .venv/bin/pip install pillow numpy")
    import hashlib
    raster = float(p.get("raster_mm", STIL["raster_mm"]))
    nokkel = hashlib.md5(f"{kilde}|{navn}|{maal[0]:.1f}|{maal[1]:.1f}|{zoom}|{raster}|{MAKS_PX}".encode()).hexdigest()[:10]
    cache = mappe / ".stil"
    cache.mkdir(exist_ok=True)
    ut = cache / f"{kilde.stem}-{navn}-{nokkel}.png"
    if not ut.exists() or ut.stat().st_mtime < kilde.stat().st_mtime or ut.stat().st_mtime < (HER / "print_style.py").stat().st_mtime:
        subprocess.run([str(VENV_PY), str(HER / "print_style.py"), str(kilde), str(ut), "--stil", navn,
                        "--panel-mm", f"{maal[0]:.2f}", f"{maal[1]:.2f}", "--zoom", str(zoom),
                        "--raster-mm", str(raster), "--maks-px", str(MAKS_PX)],
                       check=True, stdout=subprocess.DEVNULL)
    return ut.as_uri()


def rader_av(node):
    """Normaliser rader: liste av {h, paneler}."""
    ut = []
    for r in node.get("rader", []):
        if isinstance(r, list):
            ut.append({"h": 1, "paneler": r})
        else:
            ut.append({"h": r.get("h", 1), "paneler": r.get("paneler", [])})
    return ut


def panel_html(p, mappe, opt, sidenr):
    if "rader" in p:  # nøstet panelgruppe
        return f'<div class="gruppe" style="flex:{p.get("bredde", 1)}">{rader_html(p, mappe, opt, sidenr)}</div>'
    pid = esc(p.get("id", ""))
    innhold, tekster = panel_innhold(p, mappe, opt, float(p.get("zoom", 1)), p.get("fokus", "50% 50%"))
    kant = "" if p.get("kant", True) else " utenkant"
    return (f'<div class="panel{kant}" style="flex:{p.get("bredde", 1)}" data-id="{pid}">'
            f'<div class="bilde">{innhold}</div>{overlegg_html(p, mappe)}<svg class="bobler"></svg>{tekster}</div>')


def overlegg_html(p, mappe):
    """Frilagt figur (PNG med gjennomsiktighet) som ligger over rammen og kan bryte ut av panelet."""
    o = p.get("overlegg")
    if not o:
        return ""
    f = (mappe / os.path.expanduser(o.get("bilde", ""))).resolve()
    if not f.exists():
        print(f"WARNING: missing overlay {f}", file=sys.stderr)
        return ""
    return (f'<img class="overlegg" src="{f.as_uri()}" style="left:{o.get("x", 0)}%;top:{o.get("y", 0)}%;'
            f'width:{o.get("b", 100)}%">')


ANSIKT = {}


def fokus_data(mappe, o, zoom=1.0):
    """data-attributter som lar JS-en sentrere hodene til personene i fokus (se fokus.py)."""
    if not o.get("bilde") or o.get("fokus_fast"):
        return ""
    info = ANSIKT.get(str((mappe / os.path.expanduser(o["bilde"])).resolve()))
    k = fokus_mod.hodebokser(info)
    if not k:
        return ""
    return f' data-k="{json.dumps(list(k))}" data-iw="{info["b"]}" data-ih="{info["h"]}" data-z="{zoom}"'


def finn_ansikter(serie, mappe):
    stier = []

    def gaa(x):
        if isinstance(x, dict):
            if isinstance(x.get("bilde"), str):
                stier.append(str((mappe / os.path.expanduser(x["bilde"])).resolve()))
            for v in x.values():
                gaa(v)
        elif isinstance(x, list):
            for v in x:
                gaa(v)
    gaa(serie)
    ANSIKT.update(fokus_mod.finn(stier, mappe / ".ansikter.json"))


def panel_innhold(p, mappe, opt, zoom, fokus):
    """Bildet (eller plassholderen) og tekstene i et panel."""
    pid = esc(p.get("id", ""))
    url = stil_url(mappe, p, zoom) or bilde_url(mappe, p.get("bilde"))
    stil_bilde = f"object-position:{fokus};"
    if zoom != 1:
        # zoom uten transform (transform blir ikke med i PDF-utskriften): større bilde, forskjøvet mot fokuspunktet
        try:
            fx, fy = (float(v.strip().rstrip("%")) for v in fokus.split()[:2])
        except ValueError:
            fx, fy = 50.0, 50.0
        stil_bilde += (f"position:absolute;width:{zoom * 100:.2f}%;height:{zoom * 100:.2f}%;"
                       f"left:{-(zoom - 1) * fx:.2f}%;top:{-(zoom - 1) * fy:.2f}%;")
    if url:
        innhold = f'<img src="{url}" style="{stil_bilde}"{fokus_data(mappe, p, zoom)}>'
    else:
        prompt = esc((p.get("prompt") or p.get("beskrivelse") or "")[:160])
        innhold = f'<div class="plass"><b>{pid}</b><span>{prompt}</span></div>'
    if opt["rutenett"]:
        innhold += '<div class="rutenett"></div>'
    tekster = []
    for i, t in enumerate(p.get("tekst", [])):
        typ = t.get("type", "tale")
        data = {"type": typ}
        if "hale" in t:
            data["hale"] = t["hale"]
        stil = []
        if "x" in t:
            stil.append(f"left:{t['x']}%")
        if "y" in t:
            stil.append(f"top:{t['y']}%")
        if "b" in t:
            stil.append(f"width:{t['b']}%")
        if "maxb" in t:   # valgfritt: hev maksbredden (f.eks. lange ord i smale ruter)
            stil.append(f"max-width:{t['maxb']}%")
        if "str" in t:
            stil.append(f"font-size:{t['str']}pt")
        if typ == "lyd":
            stil.append(f"transform:rotate({t.get('rot', -8)}deg)")
            if "farge" in t:
                stil.append(f"color:{t['farge']}")
        if typ == "boks" and "farge" in t:
            stil.append(f"background:{t['farge']}")
        auto = "" if ("x" in t and "y" in t) else " auto"
        tekster.append(
            f'<div class="t {esc(typ)}{auto}" data-i="{i}" data-t=\'{esc(json.dumps(data))}\' style="{";".join(stil)}">'
            f'{tekst_html(t.get("tekst", ""))}</div>')
    return innhold, "".join(tekster)


def oppsett_ruter(s, fmt, utf):
    """Rutene i et ferdig oppsett, parret med panelene fra serie.json (tomme ruter får plassholder)."""
    B, H, marg, rom, _ = FORMATER[fmt]
    ruter = oppsett_mod.hent(s["oppsett"], B, H, marg, rom, utf)
    if "_tomme" not in s:  # lages én gang, så panelplan og html bruker de samme plassholder-objektene
        n = len(ruter) - len(s.get("paneler", []))
        if n < 0:
            print(f"WARNING: layout {s['oppsett']} has {len(ruter)} panels, but the page has "
                  f"{len(s['paneler'])} – the rest are dropped", file=sys.stderr)
        s["_tomme"] = [{"id": "?", "prompt": "(empty panel)"} for _ in range(max(0, n))]
    return list(zip(ruter, list(s.get("paneler", [])) + s["_tomme"]))


def fri_panel_html(rute, p, mappe, opt, dx, z):
    """Panel med fri geometri (polygon/sirkel/rotert) plassert absolutt på siden."""
    bx, by, bw, bh = oppsett_mod.bbox(rute)
    zoom = float(p.get("zoom", rute.get("zoom", 1)))
    fokus = p.get("fokus", rute.get("fokus", "50% 50%"))
    innhold, tekster = panel_innhold(p, mappe, opt, zoom, fokus)
    kant = p.get("kant", rute.get("kant", True))
    strek = "0.55"
    if rute["form"] == "sirkel":
        klipp = "circle(50% at 50% 50%)"
        form = f'<ellipse cx="{bw / 2:.3f}" cy="{bh / 2:.3f}" rx="{bw / 2:.3f}" ry="{bh / 2:.3f}"'
    else:
        pts = [((x - bx), (y - by)) for x, y in rute["p"]]
        klipp = "polygon(" + ",".join(f"{x / bw * 100:.3f}% {y / bh * 100:.3f}%" for x, y in pts) + ")"
        form = f'<polygon points="{" ".join(f"{x:.3f},{y:.3f}" for x, y in pts)}"'
    ramme = ""
    if kant:
        hvit = rute.get("hvit")
        ramme = (f'<svg class="rammesvg" viewBox="0 0 {bw:.3f} {bh:.3f}" preserveAspectRatio="none">'
                 + (f'{form} fill="none" stroke="#fff" stroke-width="{2 * hvit}" stroke-linejoin="miter"/>' if hvit else "")
                 + f'{form} fill="none" stroke="#111" stroke-width="{strek}" stroke-linejoin="miter"/></svg>')
    stil = f"left:{bx + dx:.3f}mm;top:{by + opt['utfall']:.3f}mm;width:{bw:.3f}mm;height:{bh:.3f}mm;z-index:{z}"
    rot = ""
    if rute.get("rot"):
        rcx, rcy = rute.get("rc", (bx + bw / 2, by + bh / 2))
        stil += f";transform:rotate({rute['rot']}deg);transform-origin:{rcx - bx:.3f}mm {rcy - by:.3f}mm"
        rot = f' data-rot="{rute["rot"]}"'
    myk = " myk" if p.get("myk", rute.get("myk")) else ""
    mork = float(p.get("mork", rute.get("mork", 0)) or 0)
    filt = f";filter:brightness({max(0.0, 1 - mork):.2f})" if mork else ""
    return (f'<div class="panel fri{myk}" style="{stil}" data-id="{esc(p.get("id", ""))}"{rot}>'
            f'<div class="bilde" style="clip-path:{klipp}{filt}">{innhold}</div>{ramme}{overlegg_html(p, mappe)}'
            f'<svg class="bobler"></svg>{tekster}</div>')


def fri_sider_html(s, nr, mappe, opt, serie):
    """En side (eller to, for oppslag) med ferdig oppsett."""
    B = FORMATER[opt["format"]][0]
    utf = opt["utfall"]
    par = oppsett_ruter(s, opt["format"], utf)
    oppslag = oppsett_mod.er_oppslag(s["oppsett"])
    sider = []
    for side in ([0, 1] if oppslag else [0]):
        if opt["utvalg"] is not None and (nr + side) not in opt["utvalg"]:
            continue
        deler = []
        for z, (rute, p) in enumerate(par, 1):
            bx, _, bw, _ = oppsett_mod.bbox(rute)
            if oppslag:  # hører ruta til denne siden?
                if side == 0 and bx >= B - 0.01:
                    continue
                if side == 1 and bx + bw <= B + 0.01:
                    continue
                r = dict(rute)
                if r["form"] == "poly" and utf:  # rute som slutter i falsen får utfall over falsen
                    kx = B + utf if side == 0 else B - utf
                    r["p"] = [(kx if abs(x - B) < 0.01 else x, y) for x, y in r["p"]]
                rute = r
            dx = utf - (B if side == 1 else 0)
            deler.append(fri_panel_html(rute, p, mappe, opt, dx, z))
        sidetall = f'<div class="sidetall">{nr + side}</div>' if serie.get("sidetall", True) else ""
        sider.append(f'<section class="side frisider">{"".join(deler)}{sidetall}</section>')
    return "".join(sider)


_VARSLET = set()
ENGELSK_OPPSETT = {v: k for k, v in comic_aliases.LAYOUTS.items()}


def sidenumre(serie):
    """(sidetall, side) for hver oppføring; oppslag teller to sider."""
    nr, ut = 1, []
    for s in serie.get("sider", []):
        ut.append((nr, s))
        if s.get("oppsett") and oppsett_mod.er_oppslag(s["oppsett"]):
            if nr % 2 == 1 and nr not in _VARSLET:
                _VARSLET.add(nr)
                print(f"WARNING: the spread on pages {nr}–{nr + 1} starts on a right-hand (odd) page – "
                      f"a page turn will split it. Move it by one page.", file=sys.stderr)
            nr += 2
        else:
            nr += 1
    return ut


def rader_html(node, mappe, opt, sidenr):
    deler = []
    for r in rader_av(node):
        celler = "".join(panel_html(p, mappe, opt, sidenr) for p in r["paneler"])
        deler.append(f'<div class="rad" style="flex:{r["h"]}">{celler}</div>')
    return "".join(deler)


def side_html(s, nr, mappe, opt, serie):
    typ = s.get("type", "paneler")
    sidetall = f'<div class="sidetall">{nr}</div>' if serie.get("sidetall", True) and typ == "paneler" else ""
    if typ == "tittel":
        return (f'<section class="side tittelside"><div class="tt">{esc(serie.get("tittel", ""))}</div>'
                f'<div class="tu">{esc(serie.get("undertittel", ""))}</div>'
                f'<div class="tf">{esc(s.get("tekst") or serie.get("forfatter", ""))}</div></section>')
    if typ == "tekst":
        return f'<section class="side tekstside"><div class="ts">{tekst_html(s.get("tekst", ""))}</div>{sidetall}</section>'
    if typ == "kapittel":
        url = stil_url(mappe, s, 1) or bilde_url(mappe, s.get("bilde"))
        bg = f'<img class="helbilde" src="{url}" style="object-position:{s.get("fokus", "50% 50%")}"{fokus_data(mappe, s)}>' if url else ""
        return (f'<section class="side kapittel">{bg}<div class="kt">{tekst_html(s.get("tekst", ""))}</div></section>')
    splash = " splash" if s.get("splash") else ""
    return f'<section class="side{splash}"><div class="ramme">{rader_html(s, mappe, opt, nr)}</div>{sidetall}</section>'


def omslag_html(serie, mappe):
    o = serie.get("omslag") or {}
    url = stil_url(mappe, o, 1) or bilde_url(mappe, o.get("bilde"))
    bg = f'<img class="helbilde" src="{url}" style="object-position:{o.get("fokus", "50% 50%")}"{fokus_data(mappe, o)}>' if url else '<div class="plass helbilde"><b>COVER</b></div>'
    plass = o.get("tittel_plass", "topp")
    farge = o.get("tittel_farge", "#ffd23f")
    return (f'<section class="side omslag {plass}">{bg}'
            f'<div class="ot" style="color:{farge}">{esc(serie.get("tittel", ""))}</div>'
            f'<div class="ou">{esc(serie.get("undertittel", ""))}</div>'
            f'<div class="of">{esc(serie.get("forfatter", ""))}</div></section>')


JS = r"""
const NS='http://www.w3.org/2000/svg';
function el(n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}
function ellipsePts(cx,cy,rx,ry,n){const p=[];for(let i=0;i<n;i++){const a=i/n*2*Math.PI;p.push([cx+rx*Math.cos(a),cy+ry*Math.sin(a)]);}return p;}
function poly(p){return p.map((q,i)=>(i?'L':'M')+q[0].toFixed(1)+' '+q[1].toFixed(1)).join(' ')+'Z';}
function tegn(){
 if(document.body.classList.contains('ferdig')) return;
 document.querySelectorAll('.panel').forEach(panel=>{
  const svg=panel.querySelector('svg.bobler'); const rot=!!panel.dataset.rot;
  // rotert panel: mål uten rotasjonen (offset*), ellers som før
  const R=rot?{left:0,top:0,width:panel.offsetWidth,height:panel.offsetHeight}:panel.getBoundingClientRect();
  const boks=t=>rot?{left:t.offsetLeft,top:t.offsetTop,width:t.offsetWidth,height:t.offsetHeight}:t.getBoundingClientRect();
  svg.setAttribute('width',R.width); svg.setAttribute('height',R.height);
  svg.setAttribute('viewBox',`0 0 ${R.width} ${R.height}`);
  const lagS=el('g',{}), lagF=el('g',{}); svg.appendChild(lagS); svg.appendChild(lagF);
  // automatisk plassering i leserekkefølge for bobler uten x/y
  let ax=0.04*R.width, ay=0.04*R.height, radH=0;
  panel.querySelectorAll('.t.auto').forEach(t=>{
    const r=boks(t);
    if(ax+r.width>R.width*0.96){ax=0.04*R.width; ay+=radH+0.03*R.height; radH=0;}
    t.style.left=ax+'px'; t.style.top=ay+'px'; ax+=r.width+0.05*R.width; radH=Math.max(radH,r.height);
  });
  const LW=parseFloat(getComputedStyle(document.body).getPropertyValue('--strek'))||1.4;
  const form=(deler,type)=>{ // tegn først strek (dobbel bredde) for alle deler, så fyll: gir felles omriss
    [].concat(deler).forEach(d=>{
      const s=el('path',{d,fill:'none',stroke:'#111','stroke-width':2*LW,'stroke-linejoin':'round'});
      if(type==='hvisk') s.setAttribute('stroke-dasharray', `${4*LW} ${3*LW}`);
      lagS.appendChild(s); lagF.appendChild(el('path',{d,fill:'#fff',stroke:'none'}));
    });
  };
  panel.querySelectorAll('.t').forEach(t=>{
   const d=JSON.parse(t.dataset.t); const type=d.type;
   if(type==='boks'||type==='lyd'||type==='fri') return;
   const r=boks(t); const cx=r.left-R.left+r.width/2, cy=r.top-R.top+r.height/2;
   let rx=r.width/2*1.2+4, ry=r.height/2*1.38+5; ry=Math.max(ry, rx*0.42);
   let body;
   if(type==='rop'){ const p=[];const n=Math.max(14,Math.round((rx+ry)/9));
     for(let i=0;i<n;i++){const a=i/n*2*Math.PI;const k=(i%2)?1.0:1.16;p.push([cx+rx*k*Math.cos(a),cy+ry*k*Math.sin(a)]);} body=poly(p);}
   else if(type==='tanke'){ // sky: ring av sirkler
     const n=Math.max(10,Math.round((rx+ry)/9)); let dd='';
     ellipsePts(cx,cy,rx*0.97,ry*0.95,n).forEach(q=>{const rr=Math.min(rx,ry)*0.22+4;
       dd+=`M${q[0]-rr} ${q[1]} a${rr} ${rr} 0 1 0 ${2*rr} 0 a${rr} ${rr} 0 1 0 ${-2*rr} 0 `;});
     dd+=`M${cx-rx*0.95} ${cy} a${rx*0.95} ${ry*0.9} 0 1 0 ${2*rx*0.95} 0 a${rx*0.95} ${ry*0.9} 0 1 0 ${-2*rx*0.95} 0`;
     body=dd;}
   else if(type==='tale-firkant'){ const k=Math.min(rx,ry)*0.35; const x0=cx-r.width/2-6,y0=cy-r.height/2-5,w=r.width+12,h=r.height+10;
     body=`M${x0+k} ${y0} H${x0+w-k} Q${x0+w} ${y0} ${x0+w} ${y0+k} V${y0+h-k} Q${x0+w} ${y0+h} ${x0+w-k} ${y0+h} H${x0+k} Q${x0} ${y0+h} ${x0} ${y0+h-k} V${y0+k} Q${x0} ${y0} ${x0+k} ${y0} Z`;}
   else { body=`M${cx-rx} ${cy} a${rx} ${ry} 0 1 0 ${2*rx} 0 a${rx} ${ry} 0 1 0 ${-2*rx} 0`; }
   // hale
   let hale=null;
   if(d.hale && d.hale!=='ingen'){
     const tx=d.hale[0]/100*R.width, ty=d.hale[1]/100*R.height;
     const dx=tx-cx, dy=ty-cy, L=Math.hypot(dx,dy)||1, ux=dx/L, uy=dy/L, px=-uy, py=ux;
     if(type==='tanke'){ // små sirkler mot den som tenker
       const kant=Math.hypot(rx*ux,ry*uy); [0.25,0.55,0.8].forEach((f,i)=>{const rr=[7,5,3.5][i];
         const x=cx+ux*(kant+ (L-kant)*f), y=cy+uy*(kant+(L-kant)*f);
         form(`M${x-rr} ${y} a${rr} ${rr} 0 1 0 ${2*rr} 0 a${rr} ${rr} 0 1 0 ${-2*rr} 0`,type);});
     } else {
       const b=Math.max(5,Math.min(rx,ry)*0.32), bx=cx+ux*Math.min(rx,ry)*0.5, by=cy+uy*Math.min(rx,ry)*0.5;
       const k=0.22*L; // lett krum hale
       hale=`M${bx+px*b} ${by+py*b} Q${(bx+tx)/2+px*k*0.3} ${(by+ty)/2+py*k*0.3} ${tx} ${ty} Q${(bx+tx)/2-px*k*0.05} ${(by+ty)/2-py*k*0.05} ${bx-px*b} ${by-py*b} Z`;
     }
   }
   form(hale?[body,hale]:[body],type);
  });
 });
 document.body.classList.add('ferdig');
}
document.fonts.ready.then(tegn);
"""


def lag_html(serie, mappe, opt):
    finn_ansikter(serie, mappe)
    fmt = opt["format"]
    B, H, marg, rom, pt = FORMATER[fmt]
    pt = serie.get("skrift_pt", pt)
    utf = opt["utfall"]
    PB, PH = B + 2 * utf, H + 2 * utf
    store = serie.get("store_bokstaver", True)
    stil = STIL["navn"] if STIL["navn"] != "ingen" else None
    boksfarge = serie.get("boks_farge", {"firefarge": "#f7e36b", "sorthvitt": "#ffffff", "sorthvitt-raster": "#ffffff", "gratone": "#ffffff"}.get(stil, "#f6e7a8"))
    papir = serie.get("papir", "#f4ecd6" if stil == "firefarge" else "#fff")
    f = FONTER.as_uri()
    css = f"""
@font-face{{font-family:Tekst;src:url('{f}/ComicNeue-Bold.ttf');font-weight:400 900}}
@font-face{{font-family:Tekst;src:url('{f}/ComicNeue-BoldItalic.ttf');font-style:italic;font-weight:400 900}}
@font-face{{font-family:Lyd;src:url('{f}/Bangers-Regular.ttf')}}
@page{{size:{PB}mm {PH}mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{--strek:1.3;background:#777;font-family:Tekst,sans-serif}}
@media print{{body{{background:none}}html,body{{overflow:hidden}}.side{{overflow:clip;contain:strict}}}}
.side{{width:{PB}mm;height:{PH}mm;position:relative;overflow:hidden;background:{papir};page-break-after:always;break-after:page;margin:0 auto}}
@media screen{{.side{{margin:8mm auto;box-shadow:0 2px 12px #0006}}}}
.ramme{{position:absolute;left:{utf + marg}mm;right:{utf + marg}mm;top:{utf + marg}mm;bottom:{utf + marg + 3}mm;display:flex;flex-direction:column;gap:{rom}mm}}
.splash .ramme{{left:{utf + marg * 0.6}mm;right:{utf + marg * 0.6}mm;top:{utf + marg * 0.6}mm;bottom:{utf + marg * 0.6 + 3}mm}}
.rad{{display:flex;gap:{rom}mm;min-height:0}}
.gruppe{{display:flex;flex-direction:column;gap:{rom}mm;min-width:0}}
.panel{{position:relative;min-width:0;min-height:0}}
.panel .bilde{{position:absolute;inset:0;overflow:hidden;border:0.55mm solid #111;background:#ddd}}
.panel.utenkant .bilde{{border:none}}
.panel.fri{{position:absolute}}
.panel.fri .bilde{{border:none}}
.panel.myk .bilde{{-webkit-mask-image:radial-gradient(ellipse at 50% 50%,#000 55%,transparent 100%);mask-image:radial-gradient(ellipse at 50% 50%,#000 55%,transparent 100%);background:none}}
.rammesvg{{position:absolute;inset:0;width:100%;height:100%;overflow:visible;pointer-events:none}}
.overlegg{{position:absolute;z-index:1;pointer-events:none}}
.panel img{{width:100%;height:100%;object-fit:cover;display:block}}
.plass{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2mm;padding:3mm;color:#555;background:repeating-linear-gradient(45deg,#e4e4e4 0 6px,#dadada 6px 12px);font:7pt/1.25 -apple-system,Helvetica,sans-serif;text-align:center}}
.plass b{{font-size:13pt;color:#333}}
.rutenett{{position:absolute;inset:0;background-image:linear-gradient(#f0f8 1px,transparent 1px),linear-gradient(90deg,#f0f8 1px,transparent 1px);background-size:10% 10%}}
svg.bobler{{position:absolute;left:0;top:0;overflow:visible;pointer-events:none;z-index:2}}
.t{{position:absolute;z-index:3;font-size:{pt}pt;line-height:1.18;text-align:center;color:#111;{"text-transform:uppercase;" if store else ""}max-width:42%;width:max-content;padding:0.4mm 0.6mm;letter-spacing:0.02em;text-wrap:balance}}
.t em{{font-style:italic;font-weight:900}}
.t.rop{{font-weight:900;font-size:{pt * 1.12:.1f}pt}}
.t.tanke{{font-style:italic}}
.t.hvisk{{font-weight:400;font-size:{pt * 0.9:.1f}pt}}
.t.boks{{background:{boksfarge};border:0.45mm solid #111;padding:1.2mm 1.8mm;text-align:left;max-width:55%}}
.t.lyd{{font-family:Lyd,Impact,sans-serif;font-size:{pt * 3.2:.0f}pt;color:#ffd23f;-webkit-text-stroke:0.9mm #111;paint-order:stroke fill;letter-spacing:0.03em;max-width:none;line-height:1}}
.t.fri{{max-width:80%}}
{".t.lyd{color:#fff}" if stil in ("sorthvitt", "sorthvitt-raster", "gratone") else ""}
.sidetall{{position:absolute;bottom:{utf + 4}mm;left:0;right:0;text-align:center;font:7pt Helvetica,sans-serif;color:#666}}
.helbilde{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.omslag .ot{{position:absolute;left:{utf + 8}mm;right:{utf + 8}mm;top:{utf + 12}mm;text-align:center;font-family:Lyd,Impact,sans-serif;font-size:{pt * 7.5:.0f}pt;line-height:0.95;-webkit-text-stroke:1.4mm #111;paint-order:stroke fill;letter-spacing:0.02em}}
.omslag .ou{{position:absolute;left:{utf + 10}mm;right:{utf + 10}mm;top:{utf + 12 + pt * 7.5 * 0.42}mm;text-align:center;font-family:Lyd,Impact,sans-serif;font-size:{pt * 2.2:.0f}pt;color:#fff;-webkit-text-stroke:0.6mm #111;paint-order:stroke fill;letter-spacing:0.12em}}
.omslag.bunn .ot{{top:auto;bottom:{utf + 30}mm}}
.omslag.bunn .ou{{top:auto;bottom:{utf + 20}mm}}
.omslag .of{{position:absolute;left:0;right:0;bottom:{utf + 9}mm;text-align:center;font-family:Lyd,Impact,sans-serif;font-size:{pt * 1.9:.0f}pt;color:#fff;-webkit-text-stroke:0.5mm #111;paint-order:stroke fill;letter-spacing:0.15em}}
.omslag.bunn .of{{bottom:{utf + 9}mm}}
.tittelside{{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5mm;text-align:center;padding:20mm}}
.tittelside .tt{{font-family:Lyd,Impact,sans-serif;font-size:{pt * 5:.0f}pt;letter-spacing:0.03em}}
.tittelside .tu{{font-family:Lyd,Impact,sans-serif;font-size:{pt * 1.8:.0f}pt;letter-spacing:0.1em;color:#555}}
.tittelside .tf{{font-size:{pt * 1.2:.1f}pt;margin-top:10mm}}
.tekstside .ts{{position:absolute;inset:{utf + marg + 15}mm;font-size:{pt * 1.25:.1f}pt;line-height:1.5;display:flex;flex-direction:column;justify-content:center}}
.kapittel .kt{{position:absolute;left:{utf + 10}mm;right:{utf + 10}mm;bottom:{utf + 25}mm;font-family:Lyd,Impact,sans-serif;font-size:{pt * 4.5:.0f}pt;color:#fff;-webkit-text-stroke:1mm #111;paint-order:stroke fill;text-align:center}}
"""
    sider = []
    if opt["med_omslag"] and serie.get("omslag") is not None:
        sider.append(omslag_html(serie, mappe))
    for i, s in sidenumre(serie):
        if s.get("oppsett"):
            sider.append(fri_sider_html(s, i, mappe, opt, serie))
        elif opt["utvalg"] is None or i in opt["utvalg"]:
            sider.append(side_html(s, i, mappe, opt, serie))
    return (f'<!doctype html><html lang="{esc(serie.get("språk", "en"))}"><head><meta charset="utf-8">'
            f'<title>{esc(serie.get("tittel", ""))}</title><style>{css}</style></head><body>'
            + "".join(sider) + f"<script>{fokus_mod.JS}{JS}</script></body></html>")


def panelplan(serie, fmt, skriv=True):
    """Skriv ut omtrentlig størrelse og beste bildeformat for hvert panel (for bildegenerering)."""
    B, H, marg, rom, _ = FORMATER[fmt]

    def gaa(node, w, h, ut):
        rader = rader_av(node)
        if not rader:
            return
        sum_h = sum(r["h"] for r in rader)
        tilgj_h = h - rom * (len(rader) - 1)
        for r in rader:
            rh = tilgj_h * r["h"] / sum_h
            ps = r["paneler"]
            sum_b = sum(p.get("bredde", 1) for p in ps)
            tilgj_w = w - rom * (len(ps) - 1)
            for p in ps:
                pw = tilgj_w * p.get("bredde", 1) / sum_b
                if "rader" in p:
                    gaa(p, pw, rh, ut)
                else:
                    STIL["maal"][id(p)] = (pw, rh)
                    forhold = pw / rh
                    best = min(FLOW_FORMATER, key=lambda k: abs(FLOW_FORMATER[k] - forhold) / FLOW_FORMATER[k])
                    ut.append((p.get("id", "?"), pw, rh, forhold, best, bool(p.get("bilde"))))

    for i, s in sidenumre(serie):
        if s.get("oppsett"):
            for rute, p in oppsett_ruter(s, fmt, 0):
                _, _, pw, ph = oppsett_mod.bbox(rute)
                STIL["maal"][id(p)] = (pw, ph)
                forhold = pw / ph
                best = min(FLOW_FORMATER, key=lambda k: abs(FLOW_FORMATER[k] - forhold) / FLOW_FORMATER[k])
                if skriv:
                    print(f"page {i:>3}  panel {p.get('id', '?'):<8} {pw:5.0f}×{ph:4.0f} mm  ratio {forhold:4.2f}  → make {best:<5} "
                          f"{'(has image)' if p.get('bilde') else ''}  [{ENGELSK_OPPSETT.get(s['oppsett'], s['oppsett'])}]")
            continue
        if s.get("type", "paneler") != "paneler":
            continue
        ut = []
        m = marg * (0.6 if s.get("splash") else 1)
        gaa(s, B - 2 * m, H - 2 * m - 3, ut)
        for pid, pw, ph, fh, best, har in (ut if skriv else []):
            print(f"page {i:>3}  panel {pid:<8} {pw:5.0f}×{ph:4.0f} mm  ratio {fh:4.2f}  → make {best:<5} {'(has image)' if har else ''}")


def tolk_utvalg(s):
    if not s:
        return None
    ut = set()
    for d in s.split(","):
        if "-" in d:
            a, b = d.split("-")
            ut.update(range(int(a), int(b) + 1))
        else:
            ut.add(int(d))
    return ut


def main():
    ap = argparse.ArgumentParser(description="Build a comic PDF from comic.json")
    ap.add_argument("serie", metavar="comic.json")
    ap.add_argument("--variant", help="added to the file name; use a new one for every version")
    ap.add_argument("--format", choices=list(FORMATER))
    ap.add_argument("--bleed", "--utfall", dest="utfall", type=float, default=0, help="bleed in mm (3 for print)")
    ap.add_argument("--grid", "--rutenett", dest="rutenett", action="store_true", help="10 %% grid in every panel")
    ap.add_argument("--pages", "--sider", dest="sider", help="e.g. 3 or 2-5 or 0,1,2 (0 = cover)")
    ap.add_argument("--png", action="store_true", help="also write one PNG per page")
    ap.add_argument("--plan", action="store_true", help="list panel sizes and image ratios, build nothing")
    ap.add_argument("--print-style", "--stil", dest="stil", help="none, bw-ink, bw-screentone, greyscale, four-color")
    ap.add_argument("--px", type=int, help="longest image side in the reading PDF (default 1600; 0 = full resolution). With --bleed: full resolution")
    a = ap.parse_args()
    global MAKS_PX
    MAKS_PX = a.px if a.px is not None else (0 if a.utfall else 1600)

    sti = Path(os.path.expanduser(a.serie)).resolve()
    serie = comic_aliases.normalize(json.loads(sti.read_text(encoding="utf-8")))
    mappe = sti.parent
    fmt = a.format or serie.get("format", "us")
    if a.plan:
        panelplan(serie, fmt)
        return
    STIL["navn"] = comic_aliases.print_style_name(a.stil) or serie.get("stilfilter")
    STIL["raster_mm"] = float(serie.get("raster_mm", 0.55))
    panelplan(serie, fmt, skriv=False)  # panelmål til stilfilteret
    B, H = FORMATER[fmt][:2]
    for helside in [serie.get("omslag") or {}] + [s for s in serie.get("sider", []) if s.get("type") == "kapittel"]:
        STIL["maal"][id(helside)] = (B, H)
    utvalg = tolk_utvalg(a.sider)
    opt = {"format": fmt, "utfall": a.utfall, "rutenett": a.rutenett, "utvalg": utvalg,
           "med_omslag": utvalg is None or 0 in utvalg}
    navn = (serie.get("tittel") or "Comic").replace(":", " -").replace("/", "-")
    if a.variant:
        navn += f" - {a.variant}"
    if a.rutenett:
        navn += " (grid)"
    html_sti = mappe / f"{navn}.html"
    pdf_sti = mappe / f"{navn}.pdf"
    html_sti.write_text(lag_html(serie, mappe, opt), encoding="utf-8")

    chrome = next((c for c in CHROME_KANDIDATER if c and os.path.exists(c)), None)
    if not chrome:
        sys.exit("Could not find Google Chrome/Chromium/Edge (set CHROME=/path/to/chrome). The HTML is here: " + str(html_sti))
    felles = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
              "--allow-file-access-from-files", "--virtual-time-budget=15000",
              f"--user-data-dir={tempfile.gettempdir()}/comic-builder-chrome"]
    # Trinn 1: la Chrome kjøre JS-en som tegner boblene, og lagre den ferdige siden som statisk HTML.
    # (--print-to-pdf alene skriver ut før boblene er tegnet.)
    dom = subprocess.run(felles + ["--dump-dom", html_sti.as_uri()], capture_output=True, text=True, timeout=300).stdout
    m = re.search(r'data-kutt="([^"]*)"', dom)
    if m:
        print(f"WARNING: a face does not fit and is cut in panel {m.group(1)} – make the image in the ratio --plan suggests, "
              "or set \"lock_focus\": true if the crop is intended", file=sys.stderr)
    if 'class="ferdig"' in dom:
        dom = re.sub(r"<script>.*?</script>", "", dom, flags=re.S)
        html_sti.write_text("<!doctype html>\n" + dom, encoding="utf-8")
    else:
        print("WARNING: the balloons were not drawn (the page script did not finish)", file=sys.stderr)
    if pdf_sti.exists():
        pdf_sti.unlink()
    for _ in range(3):  # Chrome gir av og til feilkode ved avslutning selv om PDF-en er skrevet
        subprocess.run(felles + [f"--print-to-pdf={pdf_sti}", html_sti.as_uri()],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
        if pdf_sti.exists() and pdf_sti.stat().st_size > 1000:
            break
    else:
        sys.exit("Chrome could not write the PDF")
    print(pdf_sti)
    if a.png:
        ut = mappe / ("pages-png" + (f" - {a.variant}" if a.variant else ""))
        ut.mkdir(exist_ok=True)
        sider_til_png(pdf_sti, ut, 1600)
        print(ut)


def sider_til_png(pdf, ut, px):
    """PDF → page001.png …: Swift/PDFKit on macOS, otherwise pdftoppm (poppler) or PyMuPDF."""
    if shutil.which("swift") and sys.platform == "darwin":
        subprocess.run(["swift", str(HER / "pdf_to_png.swift"), str(pdf), str(ut), str(px)], check=True)
        return
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-png", "-scale-to", str(px), str(pdf), str(ut / "page")], check=True)
        for f in sorted(ut.glob("page-*.png")):
            f.rename(ut / f"page{int(f.stem.split('-')[-1]):03d}.png")
        return
    kode = ("import sys,fitz;d=fitz.open(sys.argv[1]);px=int(sys.argv[3])\n"
            "for i,p in enumerate(d):\n z=px/max(p.rect.width,p.rect.height);p.get_pixmap(matrix=fitz.Matrix(z,z)).save(f'{sys.argv[2]}/page{i+1:03d}.png')")
    py = str(VENV_PY) if VENV_PY.exists() else sys.executable
    if subprocess.run([py, "-c", kode, str(pdf), str(ut), str(px)]).returncode:
        sys.exit("PNG export needs macOS, pdftoppm (poppler) or PyMuPDF (pip install pymupdf in the skill's .venv)")


if __name__ == "__main__":
    main()
