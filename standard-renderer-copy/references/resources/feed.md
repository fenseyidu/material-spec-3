# Feed Resource Rules

Use this file when the requested resource is `feed` or `Feed`.

## Identity

- Renderer template: `feed`
- Final output: `feed_503x645.png`
- Final size: `503 x 645`
- Renderer input filename: `feed.png`
- Generation source: shared `9:16` vertical master
- Text rendering, typography, CTA drawing, and final technical validation are renderer-owned.

## Generation Layout

- Every feed task uses the shared `9:16` vertical master from the splash rules. Judge this feed's layout against its derived final renderer crop.

## Derived-Crop Rules

The `9:16` master is generated with the splash prompt and its vertical-master reuse sentence. Use this feed rule for derived-crop QA and targeted regeneration only.

```text
派生的 feed 裁切顶部 `0%–26%` 为全宽文案安全区：保持连续、低纹理、低反光，并提供与已判定文字颜色相适配的稳定背景承托。CTA 按钮可叠加在主体上；底部 `89.15%–100%` 为按钮下边缘安全带：不得出现主体、关键结构、可读文字或品牌识别信息。
```

The attached mother image carries the scene content and visual style. The splash prompt provides the composition and template-safety instructions for the generated master.

For a targeted regeneration, use the failed `9:16` master as the image input and compose the single correction sentence from `references/shared/visual-qa.md`.

- The core subject group is horizontally and vertically centered inside the main visual block, with its visual center aligned to both centerlines and balanced breathing room on all sides.
  核心主体组在主视觉区内水平、垂直居中，视觉中心对齐主视觉区的水平与垂直中线，四周留白相对均衡。
- Core subjects, person faces, product bodies, and tall vertical props must not enter the title/subtitle safety area.
- The subject's highest meaningful point should sit clearly below the title/subtitle safety area's lower edge.
- The CTA button may overlay the core subject and must remain readable. The button-lower-edge safety band may contain only clean background, weak texture, weak shadow, ground, sky, or non-subject decoration.
- Before targeted regeneration, use `x=0–503`, `y=168–575` as the target composition bounds in the expected final `503 x 645` renderer crop. The button-lower-edge safety band is `y=575–645`.
- For targeted regeneration, derive the top anchor (`26%`), horizontal correction, and any required scale with `references/shared/visual-qa.md`. The prompt anchors the highest meaningful point at that top position; it does not repeat the `0%–26%` safety interval. Exception: when the actual primary product is explicitly a 台球杆 / pool cue, use `compositionMode: "poolCueDiagonal"`; preserve its scale at 100%, retain any intentional mother-image edge crop, and use only movement or whitespace correction. Its real silhouette must still keep the title area and button-lower-edge safety band clear.

## Pre-render QA

For `qaSchemaVersion: 4`, complete the `centeringMeasurement` and pixel-based `fitMeasurement` required by `references/shared/visual-qa.md`. Judge the subject group against the expected final renderer crop, not the raw generated canvas. After a targeted retry, also write the failed-candidate `retryPlan` audit record.

PASS only when:

- The derived final crop follows the written feed composition rules.
- The core subject group is horizontally and vertically centered inside the main visual block, with its visual center aligned to both centerlines and balanced breathing room on all sides.
  核心主体组在主视觉区内水平、垂直居中，视觉中心对齐主视觉区的水平与垂直中线，四周留白相对均衡。
- The target composition remains within `x=0–503`, `y=168–575`.
- The top `0%–26%` title/subtitle safety area is continuous, low-texture, low-reflection, and naturally transitioned into the scene through image-consistent environmental color, lighting, depth, and spatial layers.
- The `y=575–645` button-lower-edge safety band does not contain any part of a subject, product structure, readable text, or brand/core recognition. The CTA button itself may overlay the core subject and remains readable.
- The later template title/subtitle/CTA are not baked into the background.

FAIL when:

- The subject is visibly too high or too low in the main visual block.
- The core subject group is visibly shifted left or right inside the main visual block, or left/right breathing room is clearly unbalanced.
  核心主体组在主视觉区内明显向左或向右偏移，或左右留白明显不均衡。
- The pixel-based subject measurement exceeds the QA acceptance bounds `x=0–503`, `y=168–575` and needs a scale below `97%` of the original subject size.
- The top `0%–26%` title/subtitle safety area does not maintain a continuous, naturally transitioned copy-safe background.
- Subject content extends into the button-lower-edge safety band `y=575–645`.
- The CTA button is unreadable after overlaying the main visual.
- The candidate drifts from the reference mother image's subject, category, or scene logic.

Default fast flow: try at most one targeted regeneration for layout/readability issues. If the usable retry still fails, render with `RENDER_WITH_OBSERVATION` and state the concrete remaining issue. A targeted retry uses the failed candidate as its image input and the single correction sentence from `references/shared/visual-qa.md`; that sentence includes `主体与其承托物的接触关系、遮挡关系、接触阴影和受力逻辑必须保持；保持商品不变；保持主体组原有构图关系不变：画面中其他元素不变。`.

## Renderer Preparation

After Pre-render QA passes or is marked `RENDER_WITH_OBSERVATION` following its single targeted retry, save the template-safe background as `feed.png` in the task input folder.
