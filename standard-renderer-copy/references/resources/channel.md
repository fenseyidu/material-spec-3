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
- When the mother image intentionally crops a long, diagonal core subject at an edge, retain at least one continuous endpoint extending beyond a left, right, or lower edge of the effective material area. Do not crop it across the upper blank-buffer boundary or into `copySafe`.

## Pre-render QA

For `channel`, Pre-render QA is advisory. Record PASS/FAIL observations before preprocessing, but do not block the channel preprocessor, `material.json`, renderer, or delivery solely because of a FAIL.

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

Default fast flow: a FAIL may trigger one targeted regeneration when useful, but it never blocks preprocessing or rendering. Deliver the rendered result with any remaining QA observations.

## Renderer Preparation

After Pre-render QA, whether PASS or FAIL, use the channel preprocessor. Do not mechanically extract a fixed lower band or send the full buffered work image to renderer.

```bash
python3 <skill-dir>/scripts/prepare-channel-input.py \
  --template channel \
  --input <generated-channel-candidate.png> \
  --out material-spec-input/<task-folder>/channel.png
```

The preprocessor chooses the final `1041 x 225` crop from the sustained full-width blank/content boundary, not from the first isolated non-white pixel, and centers the detected right-side core subject group vertically whenever the available crop range permits. It rejects a channel candidate whose main visual protrudes above that boundary. Its output is the only acceptable non-direct channel input for renderer.
