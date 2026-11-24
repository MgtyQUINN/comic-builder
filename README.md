# comic-builder – an AI skill for making comics and graphic novels

Turns a screenplay, short story or idea into a finished comic: pages with panels, the same
characters on every page, real speech balloons and captions, in colour or black-and-white,
delivered as a reading PDF, a print file and a flip-book.

- **You choose the look.** Colour or black-and-white, and the inspiration: classic four-colour
  superhero comics, newspaper adventure strips (Agent X9, Rip Kirby, Modesty Blaise), ligne claire
  (Tintin), Franco-Belgian adventure, manga, noir, humour cartoons, painted or watercolour books,
  ink and wash … (see `references/styles.md`).
- **Any image AI.** Google Flow/Gemini, ChatGPT, Midjourney, Adobe Firefly, API services, local
  Stable Diffusion/Flux, or your own pictures (see `references/image-engines.md`).
- **Lettering is real text**, never part of the AI image – correct spelling in every language,
  easy to fix, easy to translate.
- **27 ready-made page layouts**, including two-page spreads, and print styles (four-colour
  halftone, pure ink, screentone, greyscale) that make every panel look printed the same way.

## Install

The skill is a folder. Put the whole `comic-builder` folder here:

| Tool | Where |
|---|---|
| Claude Code | `~/.claude/skills/comic-builder/` (or `.claude/skills/` in a project) |
| Claude app (claude.ai / desktop) | zip the folder and upload it under Settings → Capabilities → Skills |
| OpenAI Codex | `~/.codex/skills/comic-builder/` |

Then, once, inside the folder:

```bash
python3 -m venv .venv && .venv/bin/pip install pillow numpy
```

You also need **Google Chrome** (or Chromium / Microsoft Edge) – it renders the pages to PDF.
Works best on **macOS** (automatic face framing and PNG export built in). On Windows/Linux
everything works except the automatic face framing; for PNG pages install `poppler`
(`pdftoppm`) or run `.venv/bin/pip install pymupdf`.

## Use

Ask your assistant, e.g.:

> Make my short story `story.docx` into a 24-page black-and-white comic, like the old Agent X9 newspaper strips.

> Turn this screenplay into a graphic novel in classic Marvel-style four-colour.

The skill asks a few questions, agrees the look with you, shows a sketch PDF with every page
and balloon in place, makes character sheets and trial panels, and only then the rest.

## What does it cost?

The skill itself is free. Using it needs an AI assistant that can run skills (e.g. a Claude or
ChatGPT/Codex plan) and an image generator; their prices are set by those services, and some
have free quotas. Fonts: Comic Neue and Bangers, SIL Open Font License (free, also commercially).

## Folder

```
SKILL.md                 the instructions the assistant follows
references/              styles (looks), image engines, comic.json format, page rhythm, adaptation, publishing
scripts/                 build_comic.py and helpers
templates/make_comic.py  comic script as a generator (good for long books)
examples/the-lighthouse  a two-page example (comic.json + sketch PDF)
fonts/                   lettering fonts (OFL)
```

Images made by AI from a prompt alone may not be protected by copyright; your script, dialogue,
selection and layout are. See `references/publishing.md`. Never ask an image AI for other
people's characters, logos or panels.

## License

**comic-builder** by **Südow** is licensed under
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
Use it, change it and share it – also commercially – as long as you credit
"comic-builder by Südow" with a link to this repository. The fonts keep their own
SIL Open Font License (see `fonts/`). Comics you make with the skill are yours. See `NOTICE` for the credit line.
