# comic.json – the format

`build_comic.py` reads one JSON file. English field names are shown here; the original
Norwegian names (`sider`, `paneler`, `tekst` …) also work, see `scripts/comic_aliases.py`.

```json
{
  "title": "THE LONG ROAD",
  "subtitle": "A graphic novel",
  "author": "Jane Writer",
  "language": "en",
  "format": "us",
  "style": "black and white ink illustration in the tradition of classic newspaper adventure strips, …",
  "print_style": "bw-ink",
  "uppercase": true,
  "page_numbers": true,
  "characters": [
    {"name": "Mara", "reference": "characters/mara.jpg",
     "traits": "woman, 40s, short grey hair, green raincoat, satchel ALWAYS on her LEFT shoulder"}
  ],
  "cover": {"image": "panels/cover.jpg", "focus": "50% 40%", "title_position": "top",
            "title_color": "#ffd23f", "print_style": "none", "prompt": "…"},
  "pages": [ … ]
}
```

| Field | Default | Meaning |
|---|---|---|
| `format` | `us` | `us` 168×260 mm (US graphic novel), `a5` 148×210, `a4` 210×297, `album` 240×320 (Franco-Belgian) |
| `print_style` | none | `none`, `four-color`, `bw-ink`, `bw-screentone`, `greyscale` – see `styles.md`. Per panel too |
| `screen_mm` | 0.55 | distance between halftone dots on the page |
| `font_pt` | by format (us 8) | balloon lettering size |
| `uppercase` | `true` | comic-style capitals; `false` for mixed case |
| `box_color` | yellow (white in b/w) | caption box background; per box `color` |
| `paper` | white (newsprint with four-color) | page colour |
| `page_numbers` | `true` | small number at the foot of each page |
| `cover.title_position` | `top` | `top` or `bottom` |

## Pages

**Page numbering:** page 1 is a right-hand page. Even numbers are left-hand pages, seen first
after a page turn – put reveals there. Hooks go at the bottom of right-hand pages.

### Rows of panels (the basic page)

```json
{"rows": [
  {"h": 1, "panels": [ {"id": "3.1", …} ]},
  {"h": 1.3, "panels": [ {"id": "3.2", "width": 2, …}, {"id": "3.3", "width": 1, …} ]},
  [ {"id": "3.4"}, {"id": "3.5"}, {"id": "3.6"} ]
]}
```

`h` = relative row height, `width` = relative panel width. A row can be a plain list (h = 1).
A panel can itself contain `rows` (e.g. a tall panel on the left and three small ones on the right).

### Ready-made layouts

```json
{"layout": "diagonal", "panels": [ {"id": "5.1", …}, {"id": "5.2", …}, {"id": "5.3", …}, {"id": "5.4", …} ]}
```

Panels fill the layout's frames in reading order. Too few → grey placeholders; too many → dropped
(with a warning). Text positions (%) refer to the frame's bounding box, so in slanted or round
frames keep balloons inside the visible part.

| `layout` | Panels | Use |
|---|---|---|
| `six-grid` | 6 | 2 × 3, the base rhythm: conversation, calm |
| `strips` | 4 | wide strips: cinematic, landscape, travel |
| `splash` | 1 | full page, bleed: opening, turning point, climax |
| `half-page-three` | 4 | big panel on top + three below: establish, then details |
| `column-three` | 4 | tall column + three: full figure, a fall, height |
| `diagonal` | 4 | slanted gutters: speed, fights, chaos |
| `inset` | 3 | big image + two inset close-ups |
| `break-the-frame` | 4 | wide + big + two small; use `overlay` for the figure that breaks out |
| `zoom-steps` | 6 | wide + four zooming in on the same image (1 → 3.6) + wide |
| `bleed-frameless` | 4 | bleed top + two + frameless soft bottom |
| `round` | 3 | two big + a round inset (memory, gun sight, clock) |
| `nine-grid` | 9 | 3 × 3: tight beat, countdown, interrogation |
| `three-columns` | 4 | three tall columns + wide bottom: simultaneity |
| `montage` | 5 | bleed background + four tilted small pictures |
| `pause-panel` | 4 | wide + big + a small silent panel + wide |
| `tilted` | 4 | the whole grid tilts −4°: unease, panic |
| `spread-panorama` | 5 | panorama across both pages + four below |
| `spread-mirrored` | 8 | same grid on both pages: her/him, before/after |
| `spread-splash` | 3 | one image across the spread + two insets |
| `spread-diagonal` | 6 | one diagonal through both pages |
| `spread-release` | 10 | nine small on the left, one bleed image on the right |
| `spread-midfield` | 11 | six narrow on top, wide middle band, four at the bottom |
| `spread-full` | 1 | one image across both pages, nothing else |
| `spread-monologue` | 12 | wide top, four tall face panels, eyes at the bottom – same on both pages |
| `spread-contrast` | 7 | full-page splash on the left against a dense page on the right |
| `spread-two-worlds` | 11 | two tall columns + inset strips; the last three panels fade to black |
| `spread-strips-bang` | 8 | five strips on the left (build-up), a big bleed bang at bottom right |

`spread-*` layouts make **two pages** and count two page numbers. A spread must start on a
left-hand (even) page; the builder warns otherwise. Read `page-rhythm.md` before choosing.

### Other page types

- `{"splash": true, "rows": [[{"id": "7.1", …}]]}` – one big panel, narrow margin.
- `{"type": "title"}` – title page (title, subtitle, author).
- `{"type": "chapter", "text": "Chapter 2\nEdinburgh", "image": "…"}` – full-page image with a big title.
- `{"type": "text", "text": "…"}` – text page (foreword, afterword, colophon).

## Panel

```json
{"id": "3.2",
 "image": "panels/p03-2.jpg",
 "prompt": "Over-the-shoulder shot: @Mara faces @Tom across a kitchen table …",
 "focus": "40% 30%", "zoom": 1.6,
 "border": true,
 "text": [ … ]}
```

- `focus`: which point of the image stays in view when it is cropped (0 % = left/top).
- **Automatic framing** (macOS): faces are found with Apple Vision and the people in focus are
  centred with their whole head inside the panel. This overrides `focus` and lowers `zoom` until
  the head fits. If even the face cannot fit, the build prints `WARNING: a face does not fit …` –
  make the image in the ratio `--plan` suggests. `"lock_focus": true` turns this off for one panel
  (a deliberately cropped head, a hand). On Windows/Linux the automatic framing is skipped.
- `zoom`: 1–3, a close-up of part of the image (great for shot/reverse-shot from one image).
- `border: false`: no frame. `darken`: 0–1, darker image (three panels with rising `darken` = a fade-out).
- `overlay`: a cut-out PNG drawn over the frame, in % of the panel (may go outside):
  `{"image": "characters/mara-cutout.png", "x": 40, "y": -35, "w": 55}`.
- No `image` → a grey placeholder with the id and the start of the prompt.

## Lettering in the panel

Positions are % of the panel: `x`, `y` = top-left corner of the text, `w` = width. Without `x`/`y`
the text is placed automatically at the top in reading order (fine for a sketch, not for the final page).

| `type` | Looks like | Fields |
|---|---|---|
| `speech` | oval balloon with a tail | `tail: [x, y]` (where it points), `"none"` = no tail |
| `speech-box` | rounded rectangle (modern graphic novel) | `tail` |
| `thought` | cloud with small bubbles towards the thinker | `tail` |
| `shout` | jagged balloon, bolder text | `tail` |
| `whisper` | dashed outline, smaller text | `tail` |
| `caption` | rectangular box (narrator, place/time) | `color` |
| `sfx` | sound effect (Bangers, thick outline) | `size` (pt), `rot` (degrees), `color` |
| `free` | plain text, no balloon | |

`*word*` = emphasis, `\n` = line break, `size` overrides the font size for one text.
Off-panel speech: put `tail` on the panel edge (e.g. `[100, 50]`). Point tails at the chin or
mouth, never the middle of the face. The first speaker stands on the left.
