# Category Banner Resource Rules

Use this file when the requested resource is `categoryBanner`, `分类筛选 Banner`, `分类筛选Banner`, `分类筛选`, or `分类`.

## Identity

- Renderer template: `categoryBanner`
- Final output: `category_banner_1041x217.png`
- Final size: `1041 x 217`
- Renderer input filename: `categoryBanner.png`
- Text rendering, typography, rounded corners, and final technical validation are renderer-owned.

## Generation Layout

`categoryBanner` shares the same buffered-horizontal logic as `channel`.

```text
work image y 0%-55%     pure white or near-white crop buffer
work image y 55%-100%   effective material area
```

- The upper 55% is crop-only canvas and must stay empty.
- The lower 45% is the effective material area used for final template rendering.
- Keep the left copy-safe area clean and readable for later template text.
- Keep the main subject in the right-side main visual area.
- The subject should move inward toward the copySafe/mainVisual boundary while staying out of copySafe.
- Do not let the subject stick to the far right edge or leave large empty space in the main visual area.
- Keep the subject clearly below the 55% boundary and anchored near the lower display band.

## Shared Background

When the same task requests both `channel` and `categoryBanner`, reuse the single horizontal template-safe work image generated with the `channel` rules. Do not generate a separate `categoryBanner` background. Run `prepare-channel-input.py` twice against that shared work image, once with `--template channel` and once with `--template categoryBanner`.

Mention in delivery notes:

```text
categoryBanner 由 channel 横图共享生成。
```

## Pre-render QA

PASS only when:

- The 55% upper crop buffer is usable.
- The final lower 45% crop keeps the subject complete and recognizable.
- The left copy area is readable for the requested title/subtitle color.
- The subject mainly lands in the right-side main visual area and stays out of copySafe.
- The right-side composition feels balanced, without far-right sticking or excessive empty space.

FAIL when:

- The crop buffer cannot be reliably removed.
- The final lower crop cuts or damages the subject.
- Core subject content enters copySafe.
- The right-side main visual area is visually empty or the subject is stuck at the far right edge.

Default fast flow: try at most one targeted regeneration for boundary/layout issues. If the usable retry still fails, render with `RENDER_WITH_OBSERVATION` and state the concrete remaining issue.

## Renderer Preparation

After Pre-render QA passes or is marked `RENDER_WITH_OBSERVATION` following its single targeted retry, use the same horizontal preprocessor as `channel`:

```bash
python3 <skill-dir>/scripts/prepare-channel-input.py \
  --template categoryBanner \
  --input <generated-category-banner-candidate.png> \
  --out material-spec-input/<task-folder>/categoryBanner.png
```

Do not send the full buffered work image to renderer. A direct no-main-copy input at the exact `1041 x 217` Banner size bypasses this preparation.
