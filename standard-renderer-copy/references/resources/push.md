# Push Resource Rules

Use this file when the requested resource is `push`, `Push`, `消息页 Push`, or `消息页Push`.

## Identity

- Renderer template: `push`
- Final output: `push_1035x390.png`
- Final size: `1035 x 390`
- Renderer input filename: `push.png`
- Text rendering, typography, rounded corners, and final technical validation are renderer-owned.

## Generation Layout

- Keep the left title/subtitle support area readable for the requested text color.
- Keep the primary subject complete, commercially readable, and in the right main visual area, separated from the copy-safe area.
- Preserve the reference mother image's subject, category, lighting, material, color relationship, and scene logic.
- Do not place core subjects, faces, products, or tall props into the title/subtitle safety area.

## Pre-render QA

PASS only when:

- The candidate follows the written copy-safe and main-visual rules.
- The copy-safe area is clean enough for the requested title/subtitle color.
- The main subject remains complete, recognizable, and commercially readable.
- The subject does not compete with or pollute the title/subtitle area.
- The background does not contain the later template title/subtitle/CTA.

FAIL when:

- The subject invades the copy-safe area or makes text unreadable.
- The subject is cut, deformed, replaced, or weakened.
- Unrelated products, props, people, styles, or task elements appear.
- Original main campaign title/subtitle still competes with later template copy.

Default fast flow: try at most one targeted regeneration for layout/readability issues. If the usable retry still fails, render with `RENDER_WITH_OBSERVATION` and state the concrete remaining issue.

## Renderer Preparation

After Pre-render QA passes or is marked `RENDER_WITH_OBSERVATION` following its single targeted retry, save the template-safe background as `push.png` in the task input folder.
