# Popup Resource Rules

Use this file when the requested resource is `popup` or `弹窗`.

## Identity

- Renderer template: `popup`
- Final output: `popup_885x990.png`
- Final size: `885 x 990`
- image gen target aspect: `885:990` (`~0.89:1`).
- Renderer input filename: `popup.png`
- Layout guide: `references/layout-guides/popup-layout-guide.png`
- image gen owns title/subtitle text rendering. Renderer owns CTA drawing, rounded corners, dimensions, and final technical validation.

## Generation Layout

- Use `popup-layout-guide.png` as the generation-stage structure reference.
- In the generation prompt, state the canvas/aspect as `885:990` (`~0.89:1`).
- The guide controls the title/subtitle anchor, main visual block, and bottom background area. The later CTA may overlay the main visual.
- For an `885 x 990` working canvas, use the top `8%` of canvas height (`y≈79.2px`) as the ideal `titleTopAnchor`. The Pre-render QA tolerance is declared below. Use the blue guide mark as the horizontally centered, flexible title span with approximately `x=42px` and `width=802px`. Ignore the blue mark's fixed height; let the group expand downward according to copy length and preserve a clear gap before the main visual.
- The red main visual area remains the target composition anchor at approximately `x=83px`, `y=298px`, `width=720px`, `height=544px`. Place and scale the source subject so its visual center and fill follow this target rather than its original coordinates. It may rebalance downward slightly when the title group needs more vertical room while remaining complete and visually strong.
- In the guide, the bright orange-red horizontal line is a title-placement marker, blue marks the title's horizontal alignment and flexible expansion span, and the large orange rectangle marks the main visual reference. For this template, the declared `8%` titleTopAnchor overrides the guide line's original Y position. Use these colors only as placement markers, not as output colors or design blocks.
- Place the main title and subtitle within the allowed top-Y range and at the horizontal center anchor with readable contrast, faithful wording, and no clipping. Crossing the blue mark's former bottom is not a failure.
- If the title group crowds the main visual, rebalance the whole composition: move the main visual slightly downward or scale the whole title group proportionally while preserving the source subtitle typography and hierarchy. Do not change the subtitle alone. A title-top Y outside the allowed range requires one directional retry under `references/shared/visual-qa.md`; crossing the blue mark's former bottom does not.
- For a title-Y retry, use: `将主标题和副标题作为整体移动，使标题组顶部对齐画布顶部约 8% 的位置，其他画面元素保持不变。`
- For a coordinated title/main-visual retry, when the title group moves upward, move the complete main-visual subject group upward with it. When the main visual is visibly small, enlarge it by `5%-12%` (default about `10%`) while preserving the natural aspect ratio of tall or narrow products. Use: `将主标题和副标题作为整体上移，使标题组顶部对齐画布顶部约 8% 的位置；同时将完整主视觉主体组相应上移；若主体偏小，放大约 10%（不得超过 12%），保持主体自然比例、水平居中、左右留白均衡，其他画面元素保持不变。`
- The core subject group should be vertically centered inside the guide's red main visual area and scaled to fill the red area as much as possible while preserving complete recognition.
- Keep the subject large and commercially strong so the red main visual area feels well filled.
- The core subject group is horizontally centered inside the main visual block, with its visual center aligned to the block's horizontal centerline and balanced left/right breathing room.
  核心主体组在主视觉区内水平居中，视觉中心对齐主视觉区水平中线，左右留白相对均衡。
- Keep core subjects, person faces, product bodies, and tall vertical props clearly separated from the readable title/subtitle group.
- The subject's highest meaningful point should keep a clear visual gap below the actual rendered title/subtitle group.
- Prioritize a complete, strong main visual in the guide area. The later renderer CTA may overlay it; record that overlap as an observation after rendering.

## Pre-render QA

PASS only when:

- The candidate follows `popup-layout-guide.png`, or has an acceptable semantic layout deviation under `references/shared/visual-qa.md`.
- The subject lands in the guide's red main visual area, is vertically centered, and fills the red area as much as possible without losing complete recognition; semantic deviation is acceptable only when the real main visual remains complete, clear, and commercially strong.
- The core subject group is horizontally centered inside the main visual block, with its visual center aligned to the block's horizontal centerline and balanced left/right breathing room.
  核心主体组在主视觉区内水平居中，视觉中心对齐主视觉区水平中线，左右留白相对均衡。
- The title/subtitle group top falls within the target `8% ±1%` of canvas height after proportional scaling; the group remains horizontally centered, readable, unclipped, and separated from the real main visual. Its height is not checked against the blue guide shape.
- Pre-render QA judges the main visual independently of future CTA overlap.
- The CTA button is not baked into the background.

FAIL when:

- The subject is too small, clearly off-center inside the red main visual area, or leaves the red area visually empty.
- The core subject group is visibly shifted left or right inside the main visual block, or left/right breathing room is clearly unbalanced.
  核心主体组在主视觉区内明显向左或向右偏移，或左右留白明显不均衡。
- The title-group top is outside the target `8% ±1%` of canvas height after proportional scaling.
- Core subject content overlaps the migrated title/subtitle group and harms title readability or subject recognition.
- The title/subtitle group is clipped, unreadable, pressed against the canvas edge, or crowds the real main visual so severely that the title-main-visual relationship collapses.
- The title/subtitle group causes harmful layout compression; crossing the blue guide height alone is not a failure.
- The subject is visually weak or under-filled in the declared main visual area.
- The candidate drifts from the reference mother image's subject, category, or scene logic.

## Renderer Preparation

After Pre-render QA passes, including `PASS with observation`, or after the allowed one-retry title-Y warning, save the template-safe background as `popup.png` in the task input folder.
