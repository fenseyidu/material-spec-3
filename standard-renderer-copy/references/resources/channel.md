# Channel Resource Rules

Use this file when the requested resource is `channel`, `频道页中通`, or `中通`.

## Identity

- Renderer template: `channel`
- Final output: `channel_1041x225.png`
- Final size: `1041 x 225`
- Renderer input filename: `channel.png`
- Text rendering, typography, rounded corners, and final technical validation are renderer-owned.

## Generation Layout

`channel` uses a buffered horizontal work image, not a direct final-size background. The work image is `1041 x 450`.

```text
work image upper area   pure white crop buffer (aim for about 49%)
work image lower area   effective material area (~4.6:1)
```

- `49%` is a generation-layout target, not a Pre-render QA threshold. The buffer may be taller or shorter when the final crop remains usable.
- The crop buffer must be blank, and the effective material area must remain complete and commercially usable after the buffer is removed.
- The boundary between the blank buffer and the effective material area must be a straight, full-width horizontal hard edge. No core subject, face, body, product, prop, or key scene structure may protrude above that edge.
- The lower-left `copySafe` area is for later title/subtitle rendering. Keep it clean, readable, and supported by background contrast. Core subjects must not enter it.
- The lower-right `mainVisual` area holds the primary subject.
- The right-side subject should move inward toward the copySafe/mainVisual boundary while staying out of `copySafe`.
- Do not let the subject stick to the far right edge, and do not leave a large empty gap inside the right-side main visual area.
- Anchor the subject near the lower display band of the effective material area. Keep its highest meaningful point clearly below the horizontal boundary.
- When `referenceEdgeCrops` is declared, preserve every declared subject's exact exit edge(s), direction, continuity, and relative occlusion in the effective material area. Do not pull it inside to create a margin, extend unseen product, crop it across the upper blank-buffer boundary, or let it enter `copySafe`.

### Continuous-background recovery

The white buffer is only a first-generation layout scaffold. If any core subject crosses its boundary, the targeted regeneration must fill that upper area with a continuous extension of the scene background and keep the complete main visual inside the intended final crop. During Pre-render QA, visually measure the complete main visual group as normalized `left,top,right,bottom` bounds. The preprocessor then uses the group's vertical center to place the final crop; it must not infer a crop from a white boundary on this recovery path.

## Pre-render QA

For `channel`, a core subject crossing the first-generation white-buffer boundary requires one targeted regeneration using continuous-background recovery. After that retry, any remaining composition issue is recorded as `RENDER_WITH_OBSERVATION` and proceeds to renderer; use `ADVISORY_FAIL` only for a non-retry channel observation.

PASS observations include:

- A straight, full-width horizontal boundary separates the blank crop buffer from the effective material area; the exact buffer height is not a QA criterion.
- No core subject or key scene structure protrudes above that boundary.
- The final lower crop keeps the subject complete and recognizable.
- The subject mainly lands in the right-side main visual area, not in `copySafe`.
- The left copy area is readable for the requested title/subtitle color.
- The subject is not stuck to the far right edge and does not leave the main visual area visually empty.

FAIL observations include:

- The blank/content transition is not a full-width horizontal boundary, or a face, body trunk, core product, main prop, or key scene structure protrudes above it and would be cut or damaged.
- The final lower crop cuts the subject or damages recognition.
- The subject crosses into `copySafe` or pollutes title/subtitle readability.
- The right-side subject is pushed to the far right or leaves the banner unbalanced.

Default fast flow: after the one continuous-background retry, a remaining split or natural edge crop proceeds to renderer with `RENDER_WITH_OBSERVATION` and a concrete observation.

## Renderer Preparation

For a passing white-buffer candidate, use the channel preprocessor. Do not mechanically extract a fixed lower band or send the full buffered work image to renderer.

```bash
python3 <skill-dir>/scripts/prepare-channel-input.py \
  --template channel \
  --input <generated-channel-candidate.png> \
  --out material-spec-input/<task-folder>/channel.png
```

The preprocessor chooses the final `1041 x 225` crop from the sustained full-width blank/content boundary, not from the first isolated non-white pixel, and centers the detected right-side core subject group vertically whenever the available crop range permits. It rejects a channel candidate whose main visual protrudes above that boundary. Its output is the only acceptable non-direct channel input for renderer.

For a continuous-background recovery candidate, pass the QA-measured bounds instead. This path centers the final crop on the main visual vertically. Any remaining edge crop is recorded by QA rather than rejected by the preprocessor:

```bash
python3 <skill-dir>/scripts/prepare-channel-input.py \
  --template channel \
  --main-visual-bounds <left,top,right,bottom> \
  --input <generated-recovery-candidate.png> \
  --out material-spec-input/<task-folder>/channel.png
```
