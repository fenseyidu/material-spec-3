# Splash Resource Rules

Use this file when the requested resource is `splash` or `开屏`.

## Identity

- Renderer template: `splash`
- Final output: `splash_1125x1956.png`
- Final size: `1125 x 1956`
- image gen target aspect: `1125:1956` (`~0.58:1`).
- Renderer input filename: `splash.png`
- Layout guide: `references/layout-guides/splash-layout-guide.png`
- image gen owns title/subtitle text rendering. Renderer owns dimensions and final technical validation.

## Generation Layout

- Use `splash-layout-guide.png` as the generation-stage structure reference.
- In the generation prompt, state the canvas/aspect as `1125:1956` (`~0.58:1`).
- The guide controls the title/subtitle anchor and main visual block.
- Use the blue guide mark as a horizontally centered title anchor at about 88% canvas width, and use `y≈374px` on the `1125 x 1956` working canvas as the ideal `titleTopAnchor`. The acceptable title-top range is the ideal Y `±3%` of canvas height. Ignore the blue mark's fixed height; let the group expand downward while keeping generous clean whitespace above it and a clear gap before the main visual.
- Use the red guide area as the target main-visual anchor: keep the subject roughly in the middle portion of the canvas and about 82% canvas width, moving and scaling it independently of the source image's original coordinates. Allow it to rebalance downward when the title group needs more room.
- Do not add unnecessary decorative elements outside the title/subtitle area and main visual area.
- In the guide, red marks the main visual reference and blue marks the title alignment anchor. Use these colors only as placement markers, not as output colors or design blocks.
- Place the main title and subtitle within the allowed top-Y range and at the horizontal center anchor with readable contrast, faithful wording, and no clipping. Crossing the blue mark's former bottom is not a failure.
- If the title group crowds the main visual, rebalance the whole composition: move the main visual downward or scale the whole title group proportionally while preserving the source subtitle typography and hierarchy. Do not change the subtitle alone. A title-top Y outside the allowed range requires one directional retry under `references/shared/visual-qa.md`; crossing the blue mark's former bottom does not.
- The core subject group should be vertically centered inside the guide's red main visual area and scaled to fill the red area as much as possible while preserving complete recognition.
- Do not over-shrink the subject or leave the red main visual area visually empty.
- The core subject group is horizontally centered inside the main visual block, with its visual center aligned to the block's horizontal centerline and balanced left/right breathing room.
  核心主体组在主视觉区内水平居中，视觉中心对齐主视觉区水平中线，左右留白相对均衡。
- Core subjects, person faces, product bodies, and tall vertical props must not overlap or reduce the readability of the title/subtitle group.
- The subject's highest meaningful point should keep a clear visual gap below the actual rendered title/subtitle group.

## Pre-render QA

PASS only when:

- The candidate follows `splash-layout-guide.png`.
- The subject lands in the guide's red main visual area, is vertically centered, and fills the red area as much as possible without losing complete recognition.
- The core subject group is horizontally centered inside the main visual block, with its visual center aligned to the block's horizontal centerline and balanced left/right breathing room.
  核心主体组在主视觉区内水平居中，视觉中心对齐主视觉区水平中线，左右留白相对均衡。
- The title/subtitle group top falls within `y≈374px ±3%` of canvas height after proportional scaling; the group remains horizontally centered, readable, unclipped, and separated from the main visual. Its height is not checked against the blue guide shape.

FAIL when:

- The subject is too small, clearly off-center inside the red main visual area, or leaves the red area visually empty.
- The core subject group is visibly shifted left or right inside the main visual block, or left/right breathing room is clearly unbalanced.
  核心主体组在主视觉区内明显向左或向右偏移，或左右留白明显不均衡。
- The title-group top is outside `y≈374px ±3%` of canvas height after proportional scaling.
- Core subject content overlaps the migrated title/subtitle group.
- The title/subtitle group is clipped, unreadable, pressed against the canvas edge, or crowds the main visual so severely that the title-main-visual gap collapses.
- The title/subtitle group causes harmful layout compression or pushes the main visual away from its declared area center; crossing the blue guide height alone is not a failure.
- The candidate drifts from the reference mother image's subject, category, or scene logic.

## Renderer Preparation

After Pre-render QA passes, including `PASS with observation`, or after the allowed one-retry title-Y warning, save the template-safe background as `splash.png` in the task input folder.
