# Choosing the look: colour or black-and-white, and the inspiration

Read this at step 2 of SKILL.md, before any image is made. The goal is that the user and Claude
**agree on one look in plain words**, write it down once (`style` + `print_style` in comic.json)
and never change it in the middle of the book.

## The two questions

Ask them together (AskUserQuestion or one short message), in the user's language:

1. **Colour or black-and-white?**

   | Choice | `print_style` | What the page looks like |
   |---|---|---|
   | Full colour (as the image model paints it) | `none` | Modern graphic novel, painted or digital colour |
   | Classic four-colour print | `four-color` | Flat colours in steps, cyan/magenta/yellow halftone dots, black ink outlines, yellowed newsprint |
   | Black-and-white, pure ink | `bw-ink` | Only black and white, strengthened ink lines, no greys |
   | Black-and-white with screentones | `bw-screentone` | Ink, and the greys turn into black dot screens (noir, manga) |
   | Greyscale / ink and wash | `greyscale` | Ink lines with smooth grey washes |

   `print_style` is a filter that runs on every panel image when the book is built. It makes all
   panels look printed the same way, even if the image model drifts a little. A single panel can
   opt out with `"print_style": "none"` (e.g. a colour flashback in a black-and-white book).

2. **What should it feel like? Which comics do you love?**
   Offer the catalogue below as suggestions, but accept anything: a series, an artist, a decade,
   a film, or images the user owns. If they are unsure, suggest two looks that fit the story and
   make trial panels in both.

## The rule about names

Names of series, publishers and artists are **for the conversation only**. They help the user
and Claude agree on a look. They are **never written into image prompts**, for three reasons:
image services often refuse them, the result drifts towards copying someone's work, and the book
should look like its own. Translate the inspiration into **technique words** (line, ink, shadow,
colour, paper, panel rhythm) and put those in `style`. Never ask for someone else's characters,
costumes, logos or recognisable panels.

Write the agreement into the project notes, e.g.:
> Look: "like an old newspaper adventure strip (Agent X9, Rip Kirby)" → `bw-ink` + style sentence N3.

## Catalogue of looks

Each entry: what people call it → colour choice → the style sentence to paste into `style`
(technique words only) → page rhythm and lettering tips.

### Colour

**C1 Classic American four-colour comic book** (people say: Marvel or DC in the 1960s–80s, Spider-Man, Fantastic Four, Superman, Fantomet/The Phantom album covers)
- `print_style`: `four-color`, `paper` defaults to newsprint
- `style`: `classic American four-color comic book art, bold black ink outlines with varied line weight, dynamic foreshortening, heroic anatomy, flat bright colors, Ben-Day halftone dots, printed on yellowed newsprint`
- Rhythm: 5–7 panels, a splash on page 1, caption boxes in yellow, big sound effects.

**C2 Modern superhero / action, digital colour** (Marvel or DC after 2000, Ultimate-era, cinematic superhero books)
- `print_style`: `none`
- `style`: `modern American comic book art, crisp detailed inks, cinematic lighting, rich digital colouring with soft gradients and rim light, dynamic camera angles`
- Rhythm: wide "widescreen" panels, silent panels, spreads. Rectangular balloons (`speech-box`) suit it.

**C3 Ligne claire** (Tintin, Blake and Mortimer, Yoko Tsuno, Spirou)
- `print_style`: `none`
- `style`: `ligne claire comic art, clean uniform black outlines, flat even colours, no hatching, no cast shadows, detailed realistic backgrounds, Franco-Belgian album style`
- Format `album`. 4 tiers of panels, 10–12 panels a page, captions sparse, rounded balloons.

**C4 Franco-Belgian realistic adventure** (Blueberry, Thorgal, XIII, Corto Maltese in colour)
- `print_style`: `none`
- `style`: `realistic European adventure comic art, confident brush inking with hatching, earthy muted colours, atmospheric skies, cinematic wide landscapes`
- Format `album`. Wide establishing panels, 8–10 panels a page.

**C5 Humour cartoon** (Asterix, Lucky Luke, Donald Duck / Carl Barks, Smurfs, Pondus)
- `print_style`: `none`
- `style`: `humorous cartoon comic art, rounded expressive characters with big noses and feet, clean bouncy outlines, bright flat colours, simple readable backgrounds`
- Many small panels, punchline in the last panel of the page, lots of sound effects.

**C6 Painted graphic novel** (European painted albums, Heavy Metal magazine, fully painted book art)
- `print_style`: `none`
- `style`: `fully painted graphic novel illustration, visible brush texture, dramatic chiaroscuro light, rich deep colours, fine-art finish`
- Fewer, larger panels; captions instead of many balloons.

**C7 Watercolour / storybook comic** (gentle European children's comics, cosy graphic novels)
- `print_style`: `none`
- `style`: `soft watercolour comic illustration, loose pencil lines, gentle washes, warm pastel palette, white paper showing through`
- Rounded balloons, mixed-case lettering (`uppercase: false`).

**C8 Cinematic noir in colour** (crime and thriller graphic novels)
- `print_style`: `none`
- `style`: `cinematic noir graphic novel art, heavy shadows, limited palette of deep teal and amber, rain-slick streets, hard rim light, film grain`

### Black-and-white

**N1 Newspaper adventure strip** (Agent X9 / Secret Agent X-9, Rip Kirby, Modesty Blaise, The Phantom dailies, Johnny Hazard)
- `print_style`: `bw-ink`
- `style`: `black and white ink illustration in the tradition of classic newspaper adventure strips, confident brush and crow-quill pen inking, feathered shadows, crosshatching, bold spot blacks, realistic anatomy, no grey tones, white paper`
- Wide strip panels (3–4 tiers), captions that tell, white sound effects.

**N2 Newspaper strip with screentones / pulp crime** (crime pulps, 1950s digests)
- `print_style`: `bw-screentone`
- `style`: `black and white ink illustration in the tradition of classic newspaper adventure strips, confident brush and crow-quill pen inking, feathered shadows, bold spot blacks, realistic anatomy, mechanical dot screen tones in mid-greys`

**N3 Stark high-contrast noir** (Sin City-type, chiaroscuro crime)
- `print_style`: `bw-ink`
- `style`: `stark high-contrast black and white noir comic art, large solid black shapes, silhouettes, white rain and rim light cut out of black, no hatching, no greys`
- Few, big panels; text in white-on-black or plain captions.

**N4 Manga** (shōnen action, shōjo drama, seinen realism)
- `print_style`: `bw-screentone`
- `style`: `black and white manga art, clean precise pen lines, expressive eyes, speed lines, screentone shading, dramatic close-ups`
- The builder lays panels out left→right (Western reading order); Japanese right→left is not supported. Format `a5`, 5–7 panels, big reaction close-ups, sound effects inside the art.

**N5 Underground / alternative** (1960s–70s comix, crosshatched indie comics)
- `print_style`: `bw-ink`
- `style`: `underground comix style black and white pen art, dense obsessive crosshatching, lumpy expressive figures, hand-made feel`

**N6 Graphic memoir, flat black** (Persepolis-type, minimalist autobiographical books)
- `print_style`: `bw-ink`
- `style`: `minimalist black and white graphic memoir art, bold flat black shapes, simple stylised figures, no hatching, strong graphic design`
- Mixed-case lettering, calm grids, many captions.

**N7 Ink and wash** (European black-and-white albums, war and historical graphic novels)
- `print_style`: `greyscale`
- `style`: `black and white ink and grey wash illustration, brush lines, soft grey washes for light and atmosphere, realistic, white paper`

**N8 Horror** (classic horror anthologies, gothic)
- `print_style`: `bw-screentone` (or `greyscale` for a softer, foggy look)
- `style`: `gothic horror comic art, heavy black ink, dripping shadows, scratchy hatching, unsettling low angles, mechanical dot screen tones`

## Agreeing in practice

1. Ask the two questions. Suggest 1–2 looks from the catalogue that fit the story's genre.
2. Write the chosen look back in one sentence ("Black-and-white newspaper-strip ink, like the
   old Agent X9 dailies: N1") and paste the style sentence into `style` and the filter into
   `print_style`.
3. Make **3–4 trial panels** from different pages (a wide shot, a close-up, a night or dark scene,
   a crowd). If the user is torn between colour and black-and-white, build both from the same
   images:
   ```
   python3 build_comic.py comic.json --pages 1-3 --variant "trial colour" --print-style none --png
   python3 build_comic.py comic.json --pages 1-3 --variant "trial bw" --print-style bw-ink --png
   ```
4. When the user approves, **lock it**: the style sentence is pasted unchanged into every prompt,
   and the print style is set once in comic.json.

## Mixing on purpose

- A flashback can have its own look: give those panels `"print_style": "greyscale"` (or `none`)
  and add "lighter, looser linework" to their prompts.
- A colour cover on a black-and-white book works well: set `"print_style": "none"` on `cover`.
- Never let the look drift by accident: same image engine, same style sentence, same filter.
