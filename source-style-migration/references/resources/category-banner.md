# Category Banner Resource Rules

Use this file when the requested resource is `categoryBanner`, `分类筛选 Banner`, `分类筛选Banner`, `分类筛选`, or `分类`.

## Identity

- Renderer template: `categoryBanner`
- Final output: `category_banner_1041x217.png`
- Final size: `1041 x 217`
- Layout guide size: `1041 x 450`.
- Effective material area: same as `channel`, only the guide's lower non-white area, about `y=49%` to `100%` (`~4.6:1`). The final renderer crop is `1041 x 217`.
- Renderer input filename: `categoryBanner.png`
- Layout guide: `references/layout-guides/channel-layout-guide.png`
- image gen owns title/subtitle text rendering. Renderer owns rounded corners, dimensions, and final technical validation.

## Generation Layout

`categoryBanner` uses the same buffered-horizontal logic as `channel`; only the final crop size differs.

```text
guide y 0%-49%      pure white crop buffer
guide y 49%-100%    effective material area
```

- The upper white area is crop-only canvas. Keep it pure white and empty.
- The lower non-white guide area is the only effective material area. Render all background, title/subtitle, and main visual inside this area.
- The boundary between the white crop buffer and the rendered material area must be a straight horizontal hard edge.
- In the generation prompt, state that only Image 2's lower `y=49%-100%` area is rendered; the effective area ratio is about `4.6:1`.
- In the guide, red marks the main visual area and blue marks the title/subtitle area. Use these colors only as placement markers, not as output colors or design blocks.
- The lower-left blue `copySafe` mark is a horizontal title anchor, not a fixed-height box. Use approximately `x=32-546` for the title group's horizontal span, place the combined main title and subtitle left-aligned, and use `51%` of the lower effective material area's height as the ideal title-group vertical-center Y, with an acceptable range of `±3%` of that effective area's height, regardless of the source image's original title position. Its vertical extent may expand around its center as needed. Keep the group inside the rendered lower area, unclipped, readable, and separated from the core subject.
- The lower-right `mainVisual` area controls the primary subject's target position and scale. Move and scale the source subject to follow this area rather than preserving its original coordinates.
- The right-side subject should move inward toward the copySafe/mainVisual boundary while staying out of `copySafe`.
- Do not let the subject stick to the far right edge, and do not leave a large empty gap inside the right-side main visual area.
- Anchor the subject inside the lower effective material area. Keep its highest meaningful point below the horizontal boundary.

## Shared Background

`channel` and `categoryBanner` may share one horizontal template-safe background when the same task requests both. If `categoryBanner` is generated from a shared `channel` background, mention in delivery notes:

```text
categoryBanner 由 channel 横图共享生成。
```

## Pre-render QA

PASS only when:

- The upper white crop buffer stays pure white and empty.
- The horizontal boundary is straight and hard-edged.
- The final crop keeps the subject complete and recognizable.
- The subject mainly lands in the guide's red main visual area and stays separated from the left title group.
- The title/subtitle group's vertical center falls within `51% ±3%` of the lower effective material area's height; the group aligns to the guide's left blue anchor and remains left-aligned, readable, and unclipped.
- The subject is not stuck to the far right edge and does not leave the main visual area visually empty.

FAIL when:

- A face, body trunk, core product, main prop, or key scene structure enters the crop buffer and would be cut or damaged.
- The final crop cuts the subject or damages recognition.
- The subject overlaps the left title group or pollutes title/subtitle readability.
- The title-group vertical center is outside `51% ±3%` of the lower effective material area's height.
- The right-side subject is pushed to the far right or leaves the banner unbalanced.

For boundary failures, apply `Buffered Horizontal Boundary Correction` in `references/shared/visual-qa.md`.

## Renderer Preparation

After Pre-render QA passes, including `PASS with observation`, or after the allowed one-retry title-Y warning, prepare `categoryBanner.png` with the same buffered-horizontal crop optimizer used by `channel`, but target the `categoryBanner` final size (`1041 x 217`).

```bash
python3 <skill-dir>/scripts/prepare-channel-input.py \
  --template categoryBanner \
  --input <generated-categoryBanner-candidate.png> \
  --out material-spec-input/<task-folder>/categoryBanner.png
```

If visual QA, OCR, or the agent can identify the complete title/subtitle bbox, pass it with `--title-bbox x1,y1,x2,y2`; the script should then execute the crop instead of guessing the text group from pixels.

The preprocessor optimizes the `1041:217` crop window for the final category banner material:

- detect the real upper white-buffer/content boundary and report when it differs from guide `y=49%`;
- detect or receive the full left-side title/subtitle group bbox, not only one text row;
- target the title/subtitle group's vertical center at `51%` of the copySafe/effective material-area height. For `categoryBanner`, use `--title-target 0.51` because the final crop is shorter than `channel`;
- score candidate crop windows with these priorities: subject completeness, title not clipped, title distance from the ideal `51%` vertical center, avoiding white buffer in final crop, then strict guide `y=49%`.

When the migrated title/subtitle group looks visually low or high in the final `1041 x 217` output, do not accept the output only because renderer technical QA passes. Re-run preparation with a complete `--title-bbox` and keep the `categoryBanner` title target at `0.51`.

The renderer uses the same channel crop logic for `categoryBanner`; the target crop size and default title target differ (`1041 x 217`, title target `0.51`).
