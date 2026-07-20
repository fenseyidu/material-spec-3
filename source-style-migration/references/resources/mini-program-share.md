# Mini Program Share Resource Rules

Use this file when the requested resource is `miniProgramShare`, `小程序分享图`, `小程序分享`, or `分享图`.

## Identity

- Renderer template: `miniProgramShare`
- Final output: `mini_program_share_600x480.png`
- Final size: `600 x 480`
- image gen target aspect: `600:480` (`1.25:1`).
- Renderer input filename: `miniProgramShare.png`
- Layout guide: `references/layout-guides/mini-program-share-layout-guide.png`
- image gen owns title/subtitle text rendering. Renderer owns dimensions and final technical validation.
- This resource has no CTA button. Do not bake a CTA into the generated background.

## Generation Layout

- Use `mini-program-share-layout-guide.png` as the generation-stage structure reference.
- In the generation prompt, state the canvas/aspect as `600:480` (`1.25:1`).
- The guide controls the title/subtitle anchor and main visual block.
- For a `600 x 480` working canvas, use the blue guide mark as a horizontal centered anchor with approximately `x=40px` and `width=519px`, and use `y≈50px` as the ideal `titleTopAnchor`. The acceptable title-top range is the ideal Y `±3%` of canvas height. Ignore the blue mark's fixed height; let the group expand downward according to copy length while keeping clean top and side margins.
- The red main visual area remains the target composition anchor at approximately `x=74px`, `y=193px`, `width=452px`, `height=246px`. Move and scale the source subject so its visual center and fill follow this target rather than its original coordinates. It may rebalance downward slightly when the title group needs more room, provided the subject remains complete.
- Place the title/subtitle group within the allowed top-Y range and at the horizontal center anchor with readable contrast, faithful wording, and no clipping. Crossing the blue mark's former bottom is not a failure.
- In the guide, red marks the main visual reference and blue marks the title alignment anchor. Use these colors only as placement markers, not as output colors or design blocks.
- The core subject group should be centered inside the guide's red main visual area and scaled to fill the red area as much as possible while preserving complete recognition.
- Do not over-shrink the subject or leave the red main visual area visually empty.
- Core subjects, person faces, product bodies, and tall vertical props must not overlap or reduce the readability of the title/subtitle group.
- The subject's highest meaningful point should keep a clear visual gap below the actual rendered title/subtitle group.
- Keep the visible source content tied to the reference mother image; do not add unrelated task elements.

## Pre-render QA

PASS only when:

- The candidate follows `mini-program-share-layout-guide.png`.
- The title/subtitle group top falls within `y≈50px ±3%` of canvas height after proportional scaling; the group remains horizontally centered, readable, unclipped, and separated from the main visual. Its height is not checked against the blue guide shape.
- The subject lands in the guide's red main visual area, is centered, and fills the red area as much as possible without losing complete recognition.
- The subject does not compete with or pollute the title/subtitle area.
- The background does not contain a baked-in CTA button.

FAIL when:

- Core subject content overlaps or disrupts the migrated title/subtitle group.
- The title-group top is outside `y≈50px ±3%` of canvas height after proportional scaling.
- The subject is too small, clearly off-center inside the red main visual area, or leaves the red area visually empty.
- The subject is cut, deformed, replaced, or weakened.
- Unrelated products, props, people, styles, or task elements appear.
- Original main campaign title/subtitle remain in the old position, are removed, or duplicate the migrated title/subtitle.
- A CTA button is baked into the background.

## Renderer Preparation

After Pre-render QA passes, including `PASS with observation`, or after the allowed one-retry title-Y warning, save the template-safe background as `miniProgramShare.png` in the task input folder.
