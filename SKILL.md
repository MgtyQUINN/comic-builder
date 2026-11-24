---
name: comic-builder
description: Turn a screenplay, short story, synopsis or idea into a finished comic / graphic novel – pages with panels, the same characters on every page, real speech balloons, thought bubbles, captions and sound effects set as text (never baked into the AI image), in colour or black-and-white, delivered as a reading PDF, a print file with bleed and a flip-book. The user picks colour or black-and-white and the inspiration (e.g. classic Marvel four-colour, newspaper adventure strips like Agent X9, ligne claire like Tintin, manga, noir) and any image AI they like. Use whenever the user says comic, graphic novel, comic book, manga, bande dessinée, webcomic pages, "make my script into a comic", "pages with panels and speech balloons", or wants a story turned into sequential art.
---

# Comic builder

From script or idea to a finished, printable comic.

**The one rule that makes it work:** the image AI only makes *pictures* – one panel at a time,
always without any text. All lettering (balloons, captions, sound effects, titles) is set by
`scripts/build_comic.py` as real text. So the spelling is always right (also å, é, ñ, ü …), lines
can be fixed without new images, the book can be translated with the same images, and the pages
are clean and printable.

```
script / idea
  → 1 clarify  → 2 agree on the look → 3 comic script (comic.json) → 4 sketch PDF ⟶ user approves
  → 5 character sheets → 6 trial panels ⟶ user approves → 7 all panels
  → 8 lettering → 9 quality check → 10 deliver (PDF, print, flip-book)
```

Talk to the user in their language. Write image prompts in English. Lettering is in the book's language.

**Folder per comic** (create it where the user keeps their work):
`<Title>/` with `comic.json` (or `make_comic.py` → `comic.json`), `characters/`, `panels/`,
`prompts/`, and the built PDFs. Keep every version: build new ones with `--variant "<name>"`,
never overwrite a version the user has seen.

**Setup once** (in the skill folder): `python3 -m venv .venv && .venv/bin/pip install pillow numpy`
(needed for the print styles). Google Chrome, Chromium or Edge must be installed (it renders the
pages). macOS adds automatic face framing and PNG export; on Windows/Linux, PNG export needs
`pdftoppm` (poppler) or `pip install pymupdf` in the .venv.

## 1. Clarify (at most four questions)

- **Source:** a script (PDF/Fountain/FDX/docx), a short story, a synopsis, or an idea. Read it yourself.
- **Length:** trial chapter (8–12 pages, the recommended start), short comic (24–48 pages) or a
  full graphic novel (`references/adaptation.md`).
- **Format and language:** `us` (US graphic novel 168×260 mm), `a5`, `a4` or `album` (240×320).
- **Image AI:** whatever the user has – Google Flow/Gemini, ChatGPT, Midjourney, Firefly, an API,
  local Stable Diffusion, or existing pictures (`references/image-engines.md`).

## 2. Agree on the look – colour or black-and-white, and the inspiration

Read `references/styles.md`. Ask:
1. **Colour or black-and-white?** → `print_style`: `none` (full colour), `four-color` (classic
   four-colour print), `bw-ink`, `bw-screentone`, `greyscale`.
2. **What should it feel like – which comics do you love?** Offer the catalogue (classic
   four-colour superhero, modern superhero, ligne claire, Franco-Belgian adventure, humour
   cartoon, painted, watercolour, colour noir; newspaper adventure strip, pulp with screentones,
   stark noir, manga, underground, graphic memoir, ink and wash, horror) or take the user's own
   references.

Names of series, publishers and artists are only for the conversation. **Never write them into
image prompts** – translate the inspiration into technique words and put that sentence in `style`.
Say the agreement back in one sentence and record it in the project notes.

## 3. Write the comic script

Read `references/adaptation.md`, `references/page-rhythm.md` and `references/comic-json.md`.
- Split the story into pages. Every page ends with a hook; reveals go on **left-hand pages**
  (even numbers – seen only after the page turn). Page 1 is a right-hand page.
- 3–6 panels per page (average ~5), rarely more than 7. Splash only for big moments.
- **Variety:** 2–3 calm grid pages, then one that breaks the pattern. Use the ready-made layouts
  (`"layout": "diagonal"`, `"inset"`, `"round"`, `"zoom-steps"`, `"montage"`, `"spread-panorama"`,
  `"spread-monologue"` … 27 in all). Spreads always start on a left-hand page. Consider at least
  one spread per chapter.
- At most ~25 words per balloon, 2–3 balloons per panel, ~150–200 words per page. Cut film
  dialogue by about half.
- Every panel gets an `id`, a shot (wide / medium / close-up / over-the-shoulder / bird's-eye),
  a `prompt` (English) and its `text` in reading order (left→right, top→bottom; the first speaker
  stands on the left).
- Use the author's own lines, names and events. Invent nothing.

For anything longer than ~40 pages write the script as a generator: copy
`templates/make_comic.py` into the comic folder and fill in characters, places, look and pages.

## 4. Sketch PDF – and wait for approval

Build the book before there are images. Panels without an image become grey placeholders with
the id and the start of the prompt, and the lettering is already in place:

```bash
python3 <skill>/scripts/build_comic.py "<folder>/comic.json" --plan > "<folder>/plan.txt"
python3 <skill>/scripts/build_comic.py "<folder>/comic.json" --variant sketch --png
```

`--plan` lists each panel's size and the image ratio to make it in (16:9, 4:3, 1:1, 3:4, 9:16).
(With the generator: run `make_comic.py` again after `--plan`, so balloons are sized to the real
panels.) Show the sketch pages and a short page list (page → what happens). **Make no images until
the user says go.**

## 5. Character sheets

One sheet per main character (front, three-quarter, profile, 2–3 expressions, white background,
no text) in the agreed style. Use the engine's character/reference feature so faces stay the same.
Write the traits in `characters` and repeat what is easy to get wrong in every prompt
("satchel over his RIGHT shoulder"). Show the sheets before panels are made.

## 6. Trial panels

3–4 panels from different pages (wide shot, close-up, a dark scene). Build them with the print
style. If the user hesitates between colour and black-and-white, build both from the same images
(`--print-style none` / `--print-style bw-ink`, each with its own `--variant`). Lock `style` and
`print_style` when approved and never change them mid-book.

## 7. All panels

- One image per panel in the ratio from `--plan`, saved as `panels/pNN-N.jpg` (page NN, panel N);
  the prompt in `prompts/pNN-N.txt`.
- Every prompt ends with the style sentence and
  `No text, no letters, no numbers, no speech bubbles, no captions, no logos, no panel borders.`
- Ask for room for balloons: `leave calm empty space in the upper third for dialogue`.
- One image can serve several panels with different `focus` ("x% y%") and `zoom` (1–3) –
  shot/reverse-shot without new images.
- Work page by page; check each batch on a contact sheet before going on.

## 8. Lettering

Build with a grid and look at every page:

```bash
python3 <skill>/scripts/build_comic.py "<folder>/comic.json" --grid --png --pages 3-4
```

The grid shows 10 % squares in each panel. For each balloon set `x`, `y` (top-left corner in % of
the panel), `w` (width in %, so the text runs 2–4 lines) and `tail` ([x, y] in %) pointing **just
at the mouth or chin**, never into the face. Balloons must not cover faces, hands or key objects.
Captions sit in a corner (`x: 0, y: 0`). Build without `--grid` when it is right.

## 9. Quality check before delivery

Look at every page (PNG from `--png`):
- Same face, hair and clothes from panel to panel; props in the right hand / on the right side.
- No text or letters inside the AI images (remake the panel – never cover it up).
- Balloons read in the right order, tails point at the right person, no text is cut off.
- No heads cut by the panel edge (the build warns: `WARNING: a face does not fit …`).
- Each page ends with a hook; reveals come after a page turn.
Remake a panel at most twice; then tell the user what is still wrong.

## 10. Deliver

```bash
# reading PDF + page images
python3 <skill>/scripts/build_comic.py "<folder>/comic.json" --variant final --png
# flip-book (one HTML file, spreads like a printed book)
python3 <skill>/scripts/flipbook.py "<folder>/pages-png - final" "<folder>/<Title> - flip-book.html" --title "<Title>"
# print file: 3 mm bleed, full resolution
python3 <skill>/scripts/build_comic.py "<folder>/comic.json" --bleed 3 --variant print
```

Also useful: a version without lettering (empty `text` lists, `--variant "no text"`) for
translation and layout programs. For print: page count divisible by 4, see `references/publishing.md`
(copyright of AI images, ISBN, resolution).

## Scripts

| Script | What it does |
|---|---|
| `scripts/build_comic.py` | comic.json → HTML + PDF via headless Chrome (two steps: the page script draws the balloons, then a static page is printed). `--plan`, `--grid`, `--pages`, `--png`, `--bleed`, `--format`, `--variant`, `--print-style`, `--px` (reading PDF downsizes images to 1600 px; print with `--bleed` uses full resolution) |
| `scripts/comic_aliases.py` | English field names ↔ internal names |
| `scripts/print_style.py` | the print styles (Pillow + NumPy in `.venv`); dot size is computed per panel so the screen is the same size on the whole page |
| `scripts/layouts.py` | geometry of the 27 ready-made layouts |
| `scripts/focus.py`, `scripts/faces.swift` | automatic framing with Apple Vision (macOS; skipped elsewhere) |
| `scripts/pdf_to_png.swift` | PDF → page001.png … on macOS (used by `--png`) |
| `scripts/flipbook.py` | page PNGs → one self-contained flip-book HTML |
| `templates/make_comic.py` | comic script as a generator, with all looks from `styles.md` |
| `fonts/` | Comic Neue (lettering) and Bangers (sound effects, titles), both SIL OFL – free, also commercially |
