# From screenplay, short story or idea to a comic script

## How long

| Source | Comic |
|---|---|
| Idea / synopsis | first a beat list (10–20 events), show it, then pages |
| Short story (5–10,000 words) | about 20–50 pages |
| Short film script (5–15 p.) | about 8–20 pages |
| Feature script (90–120 p.) | about 100–160 pages; 1–1.5 comic pages per script page, more for action, less for talk |
| Pilot / episode | about 22–32 pages per episode |

Long works are made **chapter by chapter** (8–24 pages), each approved on its own. Always start
with a trial chapter – it reveals style and character problems before they cost 150 pages.

## From film (or prose) to page

- **One scene ≠ one page.** Split the scene into beats: every new piece of information or feeling is a panel. Build pages around the page turn: the right page ends with a question, the left page after the turn answers or reveals.
- **The camera becomes the panel framing.** Establishing shot → wide panel on top. Conversation → shot/reverse-shot in two narrow panels (the same image with different `focus`/`zoom` works). Reaction → small close-up. Climax → big panel or splash.
- **Time and motion.** Film shows movement; comics show the moment before/after. Pick the most telling moment. Several small panels = time passing slowly; one wide panel = a pause.
- **Dialogue.** Cut about half. No balloon over ~25 words; split long lines into two balloons from the same speaker. Parentheticals (sighs, smiles) become facial expressions in the prompt, not text. About 150–200 words per page at most.
- **Voice-over and title cards** → caption boxes. "EDINBURGH, 1989." in the corner of the first panel of a new scene.
- **Sound** → sound effects only where the sound matters (shot, crash, phone): BANG, CRASH, CREAK, THUD, RRRING, WHOOSH (or the book's language).
- **Transitions.** A scene change gets a place/time caption or a wide establishing panel. Cross-cutting can be two rows on the same page.
- **Reading order.** Left→right, top→bottom. Whoever speaks first stands on the left. Tails must not cross.

## Writing the script as a generator (long books)

For anything over ~40 pages, write the comic script as a small Python generator
(`templates/make_comic.py`): characters, places and the style sentence are defined once, every
prompt is assembled automatically, and the look can be switched with one argument. The template
writes `comic.json` and one prompt file per panel.

## Check the comic script before the sketch

- Does every page have one clear purpose, and does it end with something that makes you turn?
- Are the reveals on left-hand pages?
- Is every panel one moment (not two actions in one image)?
- Do the shots vary (not five medium shots in a row)?
- Is the text short enough (≤ 25 words per balloon, ≤ ~200 per page)?
- Is it the author's own story – no invented events, characters or lines?
- Song lyrics are copyrighted: describe the music in a caption instead of quoting it.
