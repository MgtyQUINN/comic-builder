# Making the panel images – any image AI works

The builder does not care where an image comes from. Every panel just needs a file at
`panels/p03-2.jpg` (or any path you put in `image`). Use whatever the user already has and likes.

## The rules that matter for every engine

1. **One image per panel, no text in it.** End every prompt with:
   `No text, no letters, no numbers, no speech bubbles, no captions, no logos, no panel borders.`
   If an image still has lettering, signs or balloons, make it again or crop it away with
   `focus`/`zoom`. Never hide it under a caption box.
2. **Right shape.** Run `build_comic.py comic.json --plan`. It lists the best ratio per panel
   (16:9, 4:3, 1:1, 3:4, 9:16). Make the image in that ratio, or the builder must crop.
3. **Same faces on every page.** Use the engine's character or reference feature (table below), and
   repeat the character's traits in every prompt ("satchel over his RIGHT shoulder").
4. **Same look on every page.** Paste the agreed `style` sentence unchanged into every prompt, and
   do not switch engines in the middle of a chapter. The `print_style` filter evens out what is left.
5. **Room for balloons.** Ask for it: "leave calm empty space in the upper third for dialogue".
6. **Resolution.** For print, the longest side should be at least ~2000 px (300 dpi on a
   146 mm wide panel needs ~1700 px). Upscale small images (e.g. Upscayl, free) before printing.
7. **Save the prompt** next to the image (`prompts/p03-2.txt`) so a panel can be remade.

## Engines

| Engine | How to keep characters the same | Notes |
|---|---|---|
| **Google Flow / Gemini (Nano Banana)** | Flow "Characters" (upload a reference, name it, write `@Name` in the prompt). In Gemini/AI Studio: attach the character sheet to each request. | Free tier is generous. Flow may stop you with "unusual activity" after very many images in one day – pause, don't push. |
| **ChatGPT / GPT image** | Upload the character sheet with every request; say "same character as the reference". | Good at following long prompts; set the aspect ratio in the request. |
| **Midjourney** | Character / omni reference (`--cref` or `--oref` with the sheet URL), style reference (`--sref`) for the look, `--ar 4:3`. | Strong style; tends to add its own flair – keep the style sentence strict. |
| **Adobe Firefly** | Style and structure reference images. | Commercially "safe" training data – useful for publishing. |
| **Leonardo / Ideogram / others** | Character reference or image prompt feature. | Check the export resolution. |
| **API services (kie.ai, fal.ai, Replicate, OpenAI, Google)** | Send the character sheet as an input/reference image with each call. | Easiest to automate many panels; costs credits – say the price before a big run. |
| **Local (Stable Diffusion, Flux, ComfyUI)** | A trained LoRA per character, or IP-Adapter / reference image nodes. | Free and private once set up; most work to set up. |
| **Existing pictures** (film stills, photos, storyboards, the user's own drawings) | – | Use directly; crop with `focus`/`zoom`. The print style makes photos read as comic art, but glowing lights can blow out in black-and-white. |

## Character sheet first

Before any panel: one sheet per main character – front, three-quarter and profile, two or three
expressions, plain white background, no text – in the agreed style. Show the sheets to the user.
Save them in `characters/<name>.jpg` and list them in comic.json under `characters`
(`name`, `reference`, `traits`). Age variants (young/old) are separate characters.

## Prompt template

```
[Shot], [@Name + key traits] [action], [place, time of day, light].
[Composition: where people stand, where the empty space for balloons is].
[The style sentence].
No text, no letters, no numbers, no speech bubbles, no captions, no logos, no panel borders.
```

Vary the shots: establishing wide, medium, medium close-up, extreme close-up (eyes, hands),
over-the-shoulder, low angle, high angle / bird's-eye, silhouette, insert (an object).

For a double-page spread: "composition for a double-page spread, nothing important in the
centre third" (the fold).

## Working in batches

- Make 3–4 trial panels first and get approval of style and faces.
- Then work page by page. After each batch make a contact sheet (or build those pages) and check:
  same faces and clothes, no text in the images, right hand / right side for props, heads not cut.
- Remake a panel at most twice; then tell the user what is still wrong.
- File names follow the panel id: panel `3.2` → `panels/p03-2.jpg`. When an engine downloads
  files with its own names, rename them by their title in the engine, never "the newest file
  in Downloads".
