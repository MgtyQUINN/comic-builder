#!/usr/bin/env python3
"""Make a flip-book (one self-contained HTML file) from the pages of a comic:
the cover alone, then two-page spreads; arrow keys or click to turn pages.

Usage: python3 flipbook.py <folder with page001.png …> <out.html> [--title "…"] [--px 1400] [--quality 80]
The pages come from:  build_comic.py <comic.json> --png
"""
import argparse
import base64
import html
import shutil
import subprocess
import tempfile
from pathlib import Path

MAL = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{tittel}</title>
<style>
*{{box-sizing:border-box;margin:0}}
body{{background:#15161a;color:#ddd;font:14px -apple-system,Helvetica,sans-serif;height:100vh;display:flex;flex-direction:column}}
header{{display:flex;justify-content:space-between;align-items:center;padding:12px 20px;border-bottom:1px solid #2a2b31}}
h1{{font:600 20px Georgia,serif;letter-spacing:.04em;color:#f2f2f2}}
button{{background:#24252b;color:#eee;border:1px solid #3a3b42;border-radius:6px;padding:7px 14px;cursor:pointer;font-size:13px}}
button:disabled{{opacity:.35;cursor:default}}
main{{flex:1;display:flex;align-items:center;justify-content:center;min-height:0;padding:14px}}
.oppslag{{display:flex;height:100%;max-width:100%;box-shadow:0 10px 40px #000a;cursor:pointer}}
.oppslag img{{height:100%;width:auto;max-width:50vw;object-fit:contain;display:block;background:#fff}}
.oppslag.ene img{{max-width:90vw}}
.oppslag img+img{{border-left:2px solid #222}}
footer{{display:flex;gap:16px;justify-content:center;align-items:center;padding:10px}}
</style></head><body>
<header><h1>{tittel}</h1><button onclick="vis(0)">Start again</button></header>
<main><div class="oppslag" id="o" onclick="neste()"></div></main>
<footer><button id="f" onclick="forrige()">← Previous</button><span id="s"></span><button id="n" onclick="neste()">Next →</button></footer>
<script>
const S={sider};
// oppslag: [0] alene (omslag), så [1,2], [3,4] …
const O=[[0]]; for(let i=1;i<S.length;i+=2) O.push(i+1<S.length?[i,i+1]:[i]);
let k=0;
function vis(i){{k=Math.max(0,Math.min(O.length-1,i));const o=document.getElementById('o');
 o.className='oppslag'+(O[k].length==1?' ene':'');o.innerHTML=O[k].map(j=>'<img src="'+S[j]+'">').join('');
 document.getElementById('s').textContent=k==0?'Cover':'Pages '+O[k].join('–')+' of '+(S.length-1);
 document.getElementById('f').disabled=k==0;document.getElementById('n').disabled=k==O.length-1;}}
function neste(){{vis(k+1)}} function forrige(){{vis(k-1)}}
document.addEventListener('keydown',e=>{{if(e.key=='ArrowRight')neste();if(e.key=='ArrowLeft')forrige();}});
vis(0);
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mappe", metavar="pages_folder")
    ap.add_argument("ut", metavar="out.html")
    ap.add_argument("--title", "--tittel", dest="tittel", default="Comic")
    ap.add_argument("--px", type=int, default=1400)
    ap.add_argument("--quality", "--kvalitet", dest="kvalitet", type=int, default=80)
    a = ap.parse_args()
    filer = sorted(Path(a.mappe).expanduser().glob("page*.png")) or sorted(Path(a.mappe).expanduser().glob("side*.png"))
    if not filer:
        raise SystemExit("No page*.png in " + a.mappe)
    sider = []
    with tempfile.TemporaryDirectory() as tmp:
        for f in filer:
            j = Path(tmp) / (f.stem + ".jpg")
            if shutil.which("sips"):
                subprocess.run(["sips", "-Z", str(a.px), "-s", "format", "jpeg", "-s", "formatOptions", str(a.kvalitet),
                                str(f), "--out", str(j)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                from PIL import Image  # pip install pillow (or run with the skill's .venv python)
                im = Image.open(f).convert("RGB"); im.thumbnail((a.px, a.px)); im.save(j, quality=a.kvalitet)
            sider.append("data:image/jpeg;base64," + base64.b64encode(j.read_bytes()).decode())
    ut = Path(a.ut).expanduser()
    ut.write_text(MAL.format(tittel=html.escape(a.tittel), sider="[" + ",".join(f'"{s}"' for s in sider) + "]"),
                  encoding="utf-8")
    print(ut, f"({len(filer)} pages, {ut.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
