# Push Resource Rules

Use this file when the requested resource is `push`, `Push`, `消息页 Push`, or `消息页Push`.

## Identity

- Renderer template: `push`
- Final output: `push_1035x390.png`
- Final size: `1035 x 390`
- image gen target aspect: `1035:390` (`~2.65:1`).
- Renderer input filename: `push.png`
- Layout guide: `references/layout-guides/push-layout-guide.png`
- image gen owns title/subtitle text rendering. Renderer owns rounded corners, dimensions, and final technical validation.

## Generation Layout

- Use `push-layout-guide.png` as the generation-stage structure reference.
- In the generation prompt, state the canvas/aspect as `1035:390` (`~2.65:1`).
- The guide controls the copy-safe/title anchor and main visual area.
- In the guide, red marks the main visual reference and blue marks the title/subtitle horizontal anchor. Ignore the blue mark's fixed height; use it only for left alignment and approximate horizontal span. Keep guide colors invisible in the output.
- Place the migrated main title and subtitle at the left title anchor with readable contrast and faithful wording. Use the guide's blue center at `y≈195px` on the `1035 x 390` working canvas as the ideal title-group vertical-center Y, with an acceptable range of `±3%` of canvas height, regardless of the source image's original title position. Let the text group expand vertically around its center as needed while keeping it unclipped and separated from the main subject.
- Move and scale the source subject so its visual center and fill follow the guide's red main-visual area rather than its original coordinates.
- Keep the primary subject complete, commercially readable, and separated from the copy-safe area.
- Do not improvise a new left/right split when the guide is available.
- Keep the visible source content tied to the reference mother image; do not add unrelated task elements.
- Do not let core subjects, faces, products, or tall props overlap or reduce the readability of the title/subtitle group.

## Pre-render QA

PASS only when:

- The candidate follows `push-layout-guide.png`.
- The title/subtitle group's vertical center falls within `y≈195px ±3%` of canvas height after proportional scaling; the group aligns horizontally with the guide's left blue anchor and remains left-aligned, readable, unclipped, and separated from the main subject. Its height is not checked against the blue guide shape.
- The main subject lands in the guide's red main visual area and remains complete, recognizable, and commercially readable.
- The subject does not compete with or pollute the title/subtitle area.
- The background does not contain a baked-in CTA button.

FAIL when:

- The subject overlaps the title/subtitle group or makes text unreadable.
- The title-group vertical center is outside `y≈195px ±3%` of canvas height after proportional scaling.
- The subject is cut, deformed, replaced, or weakened.
- Unrelated products, props, people, styles, or task elements appear.
- Original main campaign title/subtitle remain in the old position, are removed, or duplicate the migrated title/subtitle.

## Renderer Preparation

After Pre-render QA passes, including `PASS with observation`, or after the allowed one-retry title-Y warning, save the template-safe background as `push.png` in the task input folder.
