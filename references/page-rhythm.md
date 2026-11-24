# Page rhythm – variety that keeps the reader turning

Read this when the story is split into pages and before images are made. A good book
**breathes**: calm pages, fast pages, big moments and quiet pauses, in a rhythm the reader feels
without noticing it. Layout names are listed in `comic-json.md`.

## Ground rules

1. **One main image per page.** Decide which panel is the page's moment and give it the most room.
2. **Vary, but not all the time.** About 2–3 calm grid pages, then one that breaks the pattern.
   If every page breaks the pattern, there is no pattern to break.
3. **The page turn is a cut.** Surprises, reveals and big images belong on the **left-hand page**
   (even numbers) or in a spread, because they are seen only after the turn. Hooks and questions go
   at the **bottom of the right-hand page**.
4. **Spreads always start on a left-hand page.** The builder warns if not.
5. **Panel size = time.** Wide panels feel long, narrow ones fast. Many small panels slow time
   down; one big panel stops it.
6. **Reading order must be obvious.** Left→right, top→bottom; diagonals and insets must still read
   as a Z. Balloons should lead the eye onward.

## Eras of the superhero monthly – techniques worth borrowing

These are rhythms and page constructions, not drawings. Never use other people's characters,
costumes or panels.

| Era | Page construction | Use it for | Layouts |
|---|---|---|---|
| **Early 1960s** (dense storytelling) | 6–9 equal panels, much text, narrating captions, one splash on page 1 | lots of plot in little room, recaps, "meanwhile" | `six-grid`, `nine-grid`, `splash` as an opener |
| **Late 60s–70s** (classic drama) | 4–6 larger panels, full figures, a tall panel beside small ones, half pages at emotional peaks | romance, confrontations, strong reactions | `half-page-three`, `column-three`, `inset` |
| **Late 1980s** (dynamic "poster" pages) | tall narrow panels, figures breaking the frame, inset heads, slanted panels, big splashes | action, speed, a figure that must look huge – in small doses | `break-the-frame` (+ `overlay`), `diagonal`, `three-columns`, `spread-diagonal` |
| **1990s** | even more: spreads, frameless panels, montages, tilting grids | chaos, fights, dreams – rarely | `tilted`, `montage`, `spread-splash` |
| **2000s onward** (cinematic, decompressed) | wide "widescreen" panels, the same image repeated with small changes, silent panels, panoramas over the spread | conversations with subtext, suspense, mood, cities and landscapes | `strips`, `pause-panel`, `zoom-steps`, `spread-panorama`, `spread-mirrored` |

## Spreads – plan two pages as one surface

The best modern monthlies plan the left and right page to be seen together: mirrored grids,
contrast (big against dense) or a movement that starts on the left and lands at the bottom right.

| Technique | What it does | Layout |
|---|---|---|
| **Full double page**: one continuous scene, a place caption top left; the same figure can appear several times left→right so the image reads as time. Nothing important in the fold. | Establishes a new place with full force, right after a simple opening page. | `spread-full` |
| **Monologue picket fence**: wide top panel, a row of four tall narrow face panels (same face, small changes), an extreme close-up of the eyes at the bottom – the same on both pages. Repeat on the next spread while the face breaks down. | Inner struggle, confession, a long speech. Repetition makes time stand still. | `spread-monologue` |
| **Splash against a dense page**: the left page is one full image, the right a tight grid of talk or action. | The big moment breathes, the right page restores the pace. | `spread-contrast` |
| **Two worlds + fade-out**: two tall columns side by side (body / mind, here / there), strips laid over at the bottom; the right page ends in three panels getting darker until black. | Parallel realities; a chapter ending in unconsciousness or emptiness. The black panel is a hook before the turn. | `spread-two-worlds` (`darken` on the last three) |
| **Strips → bang**: five wide low strips on the left (quick cuts, eyes, hands, tightening dialogue), a tall panel and then a huge image on the right with the sound effect across it. | Build-up released in one explosion. | `spread-strips-bang` (+ a big `sfx`) |
| **Style shift for memories**: a flashback drawn in an older style (flat colours, classic grid). | Separates past and present without a caption. | own `style`/`print_style` per panel |

**Fixed rhythm of a monthly:** cover → 1–2 pages cold open (action or mystery) → recap/credits →
the story; the last page is a big quiet image ("to be continued"). Use the same rhythm for chapters.

**The fold:** in spread images nothing important sits in the middle. Ask for it in the prompt:
"composition for a double-page spread, nothing important in the centre third".

## Rhythm patterns that work

- **Build-up → release:** a dense page (`nine-grid`) right before a page turn to a splash or `spread-release`.
- **Establish → close in:** `half-page-three` or `strips` opens a new place; the next page moves in on faces (`six-grid`, `zoom-steps`).
- **Silence:** `pause-panel` or a wordless panel right before an important line.
- **Parallel action:** `three-columns`, `spread-mirrored` or `spread-two-worlds`.
- **Confession / inner struggle:** `spread-monologue`, maybe two spreads in a row.
- **Fade-out:** three equal panels with rising `darken` at the bottom of a right-hand page.
- **Memory and thought:** a `round` inset, a frameless soft panel (`bleed-frameless`).
- **Chaos:** `diagonal` or `tilted` – at most one such page in a row.

## Check before images are made

- Run `--plan`: every page has a clear main panel and the image ratios make sense.
- No more than 2–3 identical layouts in a row.
- Splash/spread: at most one per chapter (`spread-splash` at most once per book).
- Reveals on left-hand pages, hooks at the bottom of right-hand pages.
- Consider at least one spread per chapter.
