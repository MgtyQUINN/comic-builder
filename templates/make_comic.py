#!/usr/bin/env python3
"""Comic script as a generator → comic.json (+ one prompt file per panel).

Copy this file into the comic's folder and edit TITLE, LOOK, CHARACTERS, PLACES and PAGES.
Characters, places and the style sentence are written once; every image prompt is assembled
from them, so the whole book stays consistent and the look can be changed with one argument.

  python3 make_comic.py                       # uses LOOK below
  python3 make_comic.py --look C3             # try another look from references/styles.md
  python3 <skill>/scripts/build_comic.py comic.json --plan > plan.txt
  python3 make_comic.py                       # again: balloons are now sized to the real panels
  python3 <skill>/scripts/build_comic.py comic.json --variant sketch --png

Panel images are picked up automatically when panels/pNN-N.jpg exists (page NN, panel N).
"""
import argparse
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

TITLE = "THE LIGHTHOUSE"
SUBTITLE = "A short comic"
AUTHOR = "Your Name"
LANGUAGE = "en"
FORMAT = "us"
LOOK = "N1"   # see LOOKS (from references/styles.md)

# id → (style sentence, print_style). Technique words only – never names of series or artists.
LOOKS = {
    "C1": ("classic American four-color comic book art, bold black ink outlines with varied line weight, dynamic "
           "foreshortening, heroic anatomy, flat bright colors, Ben-Day halftone dots, printed on yellowed newsprint", "four-color"),
    "C2": ("modern American comic book art, crisp detailed inks, cinematic lighting, rich digital colouring with soft "
           "gradients and rim light, dynamic camera angles", "none"),
    "C3": ("ligne claire comic art, clean uniform black outlines, flat even colours, no hatching, no cast shadows, "
           "detailed realistic backgrounds, Franco-Belgian album style", "none"),
    "C4": ("realistic European adventure comic art, confident brush inking with hatching, earthy muted colours, "
           "atmospheric skies, cinematic wide landscapes", "none"),
    "C5": ("humorous cartoon comic art, rounded expressive characters with big noses and feet, clean bouncy outlines, "
           "bright flat colours, simple readable backgrounds", "none"),
    "C6": ("fully painted graphic novel illustration, visible brush texture, dramatic chiaroscuro light, rich deep "
           "colours, fine-art finish", "none"),
    "C7": ("soft watercolour comic illustration, loose pencil lines, gentle washes, warm pastel palette, white paper "
           "showing through", "none"),
    "C8": ("cinematic noir graphic novel art, heavy shadows, limited palette of deep teal and amber, rain-slick streets, "
           "hard rim light, film grain", "none"),
    "N1": ("black and white ink illustration in the tradition of classic newspaper adventure strips, confident brush "
           "and crow-quill pen inking, feathered shadows, crosshatching, bold spot blacks, realistic anatomy, no grey "
           "tones, white paper", "bw-ink"),
    "N2": ("black and white ink illustration in the tradition of classic newspaper adventure strips, confident brush "
           "and crow-quill pen inking, feathered shadows, bold spot blacks, realistic anatomy, mechanical dot screen "
           "tones in mid-greys", "bw-screentone"),
    "N3": ("stark high-contrast black and white noir comic art, large solid black shapes, silhouettes, white rain and "
           "rim light cut out of black, no hatching, no greys", "bw-ink"),
    "N4": ("black and white manga art, clean precise pen lines, expressive eyes, speed lines, screentone shading, "
           "dramatic close-ups", "bw-screentone"),
    "N5": ("underground comix style black and white pen art, dense obsessive crosshatching, lumpy expressive figures, "
           "hand-made feel", "bw-ink"),
    "N6": ("minimalist black and white graphic memoir art, bold flat black shapes, simple stylised figures, no "
           "hatching, strong graphic design", "bw-ink"),
    "N7": ("black and white ink and grey wash illustration, brush lines, soft grey washes for light and atmosphere, "
           "realistic, white paper", "greyscale"),
    "N8": ("gothic horror comic art, heavy black ink, dripping shadows, scratchy hatching, unsettling low angles, "
           "mechanical dot screen tones", "bw-screentone"),
}
END = "No text, no letters, no numbers, no speech bubbles, no captions, no logos, no panel borders."

# Name → traits. Write @Name in a panel's action; the traits are added to the prompt automatically.
# Repeat what is easy to get wrong (which hand, which shoulder, which leg).
CHARACTERS = {
    "Ada": "woman in her sixties, short white hair, weathered face, thick navy wool sweater, yellow oilskin coat, "
           "rubber boots, a brass key on a cord around her neck",
    "Leo": "boy of about ten, curly dark hair, oversized red raincoat, carries a small torch in his LEFT hand",
}

PLACES = {
    "rock": "a small rocky island in a grey northern sea, a white lighthouse with a red top, wind and spray",
    "lamp": "the lamp room at the top of an old lighthouse, a huge glass lens, iron railings, storm outside",
    "boat": "a small wooden rowing boat on rough dark water at night",
}

# ------------------------------------------------------------------ helpers
TAIL = {"l": [28, 62], "ll": [12, 62], "m": [50, 62], "r": [72, 62], "rr": [88, 62],
        "out-l": [0, 55], "out-r": [100, 55], "out-top": [55, 0], "out-bottom": [55, 100], "none": "none"}


def say(text, tail="m", kind="speech"):
    """Speech balloon. tail: l, ll, m, r, rr (where the speaker's mouth is) or out-l/out-r (off panel)."""
    return {"type": kind, "text": text, "tail": TAIL[tail]}


def think(text, tail="m"):
    return say(text, tail, "thought")


def shout(text, tail="m"):
    return say(text, tail, "shout")


def whisper(text, tail="m"):
    return say(text, tail, "whisper")


def caption(text, **pos):
    """Narrator / place-time box. pos: x, y, w (% of the panel) override the automatic position."""
    return {"type": "caption", "text": text, **({"_pos": pos} if pos else {})}


def sfx(text, size=16, rot=-8):
    return {"type": "sfx", "text": text, "size": size, "rot": rot}


class At(str):
    """A different place than the page's: At("boat") among a panel's texts."""


def P(shot, action, *texts, width=1, **extra):
    """One panel. extra: focus, zoom, darken, lock_focus, same_as="p02-4" (reuse another panel's image)."""
    place = next((x for x in texts if isinstance(x, At)), None)
    texts = [x for x in texts if not isinstance(x, At)]
    return {"_shot": shot, "_action": action, "_place": place, "text": texts, "width": width, **extra}


def Row(*panels, h=1):
    return {"h": h, "panels": list(panels)}


def Page(place, *rows, splash=False):
    return {"_place": place, "rows": list(rows), **({"splash": True} if splash else {})}


def Layout(place, layout, *panels):
    """A page (or spread) with a ready-made layout, e.g. "six-grid", "diagonal", "spread-panorama"."""
    return {"_place": place, "layout": layout, "panels": list(panels)}


# ------------------------------------------------------------------ the comic
# Page 1 is a right-hand page. Reveals go on even (left-hand) pages, hooks at the bottom of odd pages.
PAGES = [
    Page("rock",
         Row(P("Establishing wide shot", "the lighthouse on its rock under a black storm sky, a single lit window",
               caption("The last night of the lighthouse.")), h=1.2),
         Row(P("Medium shot", "@Ada climbs the spiral stairs with a storm lantern, breathing hard",
               At("lamp"), caption("Ada had climbed these stairs every night for forty years.")),
             P("Close-up", "@Ada's hand turns the brass key in the lamp mechanism", At("lamp"), sfx("CLUNK", 14))),
         Row(P("Wide shot", "@Ada at the dark lamp, the great lens does not light up, rain lashing the glass",
               At("lamp"), say("Come on, old girl. Not tonight.", "l")), h=1.1)),
    Layout("lamp", "six-grid",
           P("Medium close-up", "@Ada bangs the side of the mechanism with her palm", shout("Light!", "m")),
           P("Insert", "the dead lens, black glass, a storm outside"),
           P("Point of view through the rain", "far out on the black water, a tiny torch light blinking", At("boat")),
           P("Close-up", "@Ada's eyes widen as she sees the blinking light", think("Someone is out there.", "m")),
           P("Medium shot", "@Leo in a small rowing boat on rough water, holding up his torch, terrified", At("boat"),
             say("Hello? HELLO?", "m")),
           P("Close-up", "@Ada pulls the brass key from around her neck, decided")),
]


# ------------------------------------------------------------------ build comic.json
def character_text(text):
    names = [n for n in CHARACTERS if re.search(rf"@{n}\b", text)]
    return " ".join(f"@{n}: {CHARACTERS[n]}." for n in names)


def make_prompt(p, place, style):
    parts = [f"{p['_shot']}, {p['_action']}.", f"Setting: {PLACES[p['_place'] or place]}."]
    c = character_text(p["_action"])
    if c:
        parts.append(c)
    kinds = {x["type"] for x in p["text"]}
    if kinds - {"caption", "sfx"}:
        parts.append("Leave calm empty space in the upper part of the frame for speech balloons.")
    elif "caption" in kinds:
        parts.append("Keep the upper left corner calm for a caption.")
    parts += [style + ".", END]
    return " ".join(parts)


def place_texts(texts, pw=70.0, ph=75.0):
    """Rough lettering layout from the panel's size in mm (from plan.txt): captions top left,
    balloons stepped down on the speaker's side. Fine-tune later with --grid."""
    out = [dict(x) for x in texts]
    y = 0.0
    for x in [x for x in out if x["type"] == "caption"]:
        wmm = min(pw * 0.62, max(22, math.sqrt(len(x["text"])) * 8))
        lines = math.ceil(len(x["text"]) * 2.1 / wmm)
        x.update(x=0, y=round(y / ph * 100, 1), w=round(wmm / pw * 100, 1))
        y += lines * 3.3 + 3
    y += 3
    balloons = [x for x in out if x["type"] not in ("caption", "sfx")]
    for i, x in enumerate(balloons):
        n = len(x["text"])
        wmm = min(pw * 0.46 if pw > 40 else pw * 0.8, max(16, math.sqrt(n) * 6.5))
        height = math.ceil(n * 1.8 / wmm) * 3.4 + 4
        tx = x["tail"][0] if isinstance(x["tail"], list) else 50
        if len(balloons) == 1 and tx == 50:
            bx = (pw - wmm) / 2
        else:
            bx = pw * 0.05 if tx < 50 else (pw - wmm - pw * 0.05 if tx > 50 else (pw * 0.06 if i % 2 == 0 else pw * 0.5))
        bx = max(pw * 0.02, min(bx, pw * 0.98 - wmm))
        x.update(x=round(bx / pw * 100, 1), y=round(y / ph * 100, 1), w=round(wmm / pw * 100, 1))
        if isinstance(x["tail"], list) and 0 < x["tail"][0] < 100 and 0 < x["tail"][1] < 100:
            x["tail"] = [x["tail"][0], round(min(x["tail"][1], (y + height) / ph * 100 + 12), 1)]
        y += height + 4
    for x in out:
        if x["type"] == "sfx":
            x.update(x=60, y=70)
        if "_pos" in x:
            x.update(x.pop("_pos"))
    return out, y > ph * 0.85


SIZES = {}


def read_plan():
    plan = HERE / "plan.txt"
    if plan.exists():
        for m in re.finditer(r"panel (\S+)\s+(\d+)×\s*(\d+) mm", plan.read_text()):
            SIZES[m.group(1)] = (float(m.group(2)), float(m.group(3)))


def main():
    read_plan()
    ap = argparse.ArgumentParser()
    ap.add_argument("--look", choices=list(LOOKS), default=LOOK)
    a = ap.parse_args()
    style, print_style = LOOKS[a.look]

    pages, warnings, prompts = [], [], {}
    for s in PAGES:
        nr = len(pages) + 1
        spread = s.get("layout", "").startswith("spread-")
        if spread and nr % 2:
            warnings.append(f"p. {nr}: the spread '{s['layout']}' starts on a right-hand page")
        count, words = [0], [0]

        def panel(p):
            count[0] += 1
            i = count[0]
            for x in p["text"]:
                n = len(re.findall(r"\w+", x["text"]))
                words[0] += n
                if n > 25:
                    warnings.append(f"p. {nr} panel {i}: {n} words in one balloon")
            pid, name = f"{nr}.{i}", f"p{nr:02d}-{i}"
            text, full = place_texts(p["text"], *SIZES.get(pid, (70.0, 75.0)))
            if full:
                warnings.append(f"p. {nr} panel {i}: the lettering may not fit")
            out = {"id": pid, "text": text}
            src = p.get("same_as")
            if src:
                out["prompt"] = f"(same image as {src}) " + prompts.get(src, "")
                if (HERE / "panels" / f"{src}.jpg").exists():
                    out["image"] = f"panels/{src}.jpg"
            else:
                out["prompt"] = make_prompt(p, s["_place"], style)
                prompts[name] = out["prompt"]
                (HERE / "prompts").mkdir(exist_ok=True)
                (HERE / "prompts" / f"{name}.txt").write_text(out["prompt"] + "\n", encoding="utf-8")
                if (HERE / "panels" / f"{name}.jpg").exists():
                    out["image"] = f"panels/{name}.jpg"
            for k in ("focus", "zoom", "darken", "lock_focus"):
                if k in p:
                    out[k] = p[k]
            if p.get("width", 1) != 1:
                out["width"] = p["width"]
            return out

        if "layout" in s:
            page = {"layout": s["layout"], "panels": [panel(p) for p in s["panels"]]}
        else:
            page = {"rows": [{"h": r["h"], "panels": [panel(p) for p in r["panels"]]} for r in s["rows"]]}
            if s.get("splash"):
                page["splash"] = True
        if words[0] > (400 if spread else 200):
            warnings.append(f"p. {nr}: {words[0]} words on the page")
        pages.append(page)
        if spread:
            pages.append(None)   # a spread counts as two pages
    pages = [x for x in pages if x is not None]

    comic = {
        "title": TITLE, "subtitle": SUBTITLE, "author": AUTHOR, "language": LANGUAGE, "format": FORMAT,
        "style": style, "print_style": print_style, "uppercase": True, "page_numbers": True,
        "characters": [{"name": n, "traits": t, **({"reference": f"characters/{n.lower()}.jpg"}
                        if (HERE / "characters" / f"{n.lower()}.jpg").exists() else {})}
                       for n, t in CHARACTERS.items()],
        "cover": {"title_position": "top", "title_color": "#ffd23f",
                  "prompt": f"Portrait comic book cover illustration: @Ada ({CHARACTERS['Ada']}) holds a lantern high at "
                            f"the top of the lighthouse in a storm, dark sky in the upper third for the title. {style}. {END}"},
        "pages": pages,
    }
    if (HERE / "panels" / "cover.jpg").exists():
        comic["cover"]["image"] = "panels/cover.jpg"
    (HERE / "comic.json").write_text(json.dumps(comic, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(1 for _ in (HERE / "prompts").glob("*.txt"))
    print(f"{HERE / 'comic.json'}: {len(pages)} pages, {n} prompts, look {a.look} ({print_style})")
    for w in warnings:
        print("WARNING:", w)


if __name__ == "__main__":
    main()
