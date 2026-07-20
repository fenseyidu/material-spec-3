# Splash Resource Rules

Use this file when the requested resource is `splash` or `开屏`.

## Identity

- Renderer template: `splash`
- Final output: `splash_1125x1956.png`
- Final size: `1125 x 1956`
- Renderer input filename: `splash.png`
- Fixed generation canvas: `9:16` (also the shared vertical-master canvas)
- Text rendering, typography, and final technical validation are renderer-owned.

## Generation Layout

- On the AI image-generation path, always generate exactly at `9:16`; do not follow the reference image's aspect ratio. Apply the naturally blended title/subtitle safety zone defined below before placing the centered main visual block.
- When at least one of `feed` or `popup` is requested with splash, this is the one shared vertical master. Extend its continuous copy-safe area and validate the derived feed/popup crops before rendering; do not generate additional feed/popup backgrounds.

## Prompt Text

When assembling the prompt, use these sentences in order, replacing placeholders with the current request's actual subjects and resolved text-color support:

```text
需求：基于参考图，生成一张 9:16 比例的图片。
构图：<核心主体>组成核心主体组，核心主体组置于画面中水平居中、垂直居中，四周留白均衡。
顶部 16%–35% 为全宽文案安全区：保持连续、低纹理、低反光，并提供与已判定文字颜色相适配的稳定背景承托；沿用原图的环境色、光影、景深与空间层次，以柔和渐变自然过渡并融入主体区。
若参考母图中长条斜向核心主体有意延伸至画布外，保留至少一个连续端部出画的构图；不得为完整展示而缩小或收回主体，仍须避开文案安全区。
```

For a vertical-master combination, append this sentence to the splash prompt before generation:

```text
竖版母图复用：为 feed、弹窗和开屏的最终裁切共同保留连续、低纹理、低反光的文案承托区；核心主体组完整落在各裁切结果共同可用的主视觉区域，底部为 feed、弹窗的按钮下边缘安全带保留干净背景。
```

- The core subject group is horizontally and vertically centered inside the main visual block, with its visual center aligned to both centerlines and balanced breathing room on all sides.
  核心主体组在主视觉区内水平、垂直居中，视觉中心对齐主视觉区的水平与垂直中线，四周留白相对均衡。
- Core subjects, person faces, product bodies, and tall vertical props must not enter the title/subtitle safety area.
- The subject's highest meaningful point should sit clearly below the title/subtitle safety area's lower edge.

## Pre-render QA

For `qaSchemaVersion: 4`, complete the `centeringMeasurement` required by `references/shared/visual-qa.md`. Judge the subject group against the expected final renderer crop, not the raw generated canvas.

PASS only when:

- The candidate follows the written `9:16` composition rules.
- The core subject group is horizontally and vertically centered inside the main visual block, with its visual center aligned to both centerlines and balanced breathing room on all sides.
  核心主体组在主视觉区内水平、垂直居中，视觉中心对齐主视觉区的水平与垂直中线，四周留白相对均衡。
- The top `16%–35%` title/subtitle safety area is continuous, low-texture, low-reflection, and naturally transitioned into the scene through image-consistent environmental color, lighting, depth, and spatial layers.
- The later template title/subtitle are not baked into the background.

FAIL when:

- The subject is visibly too high or too low in the main visual block.
- The core subject group is visibly shifted left or right inside the main visual block, or left/right breathing room is clearly unbalanced.
  核心主体组在主视觉区内明显向左或向右偏移，或左右留白明显不均衡。
- The top `16%–35%` title/subtitle safety area does not maintain a continuous, naturally transitioned copy-safe background.
- The candidate drifts from the reference mother image's subject, category, or scene logic.

Default fast flow: try at most one targeted regeneration for layout/readability issues. If the usable retry still fails, render with `RENDER_WITH_OBSERVATION` and state the concrete remaining issue. Derive the `35%` top anchor, horizontal correction, and any required scale from the actual candidate using `references/shared/visual-qa.md`; name the actual core subject instead of writing `核心主体组`. The targeted prompt must anchor the highest meaningful point at approximately `35%` from the top and require horizontal centering; it must not repeat the `16%–35%` safety interval or pair the anchor with `垂直居中`. Append `主体与其承托物的接触关系、遮挡关系、接触阴影和受力逻辑必须保持；保持商品不变；画面中其他元素不变。` Do not add `保持商品不变` as a QA check or repeat the full generation prompt.

## Renderer Preparation

After Pre-render QA passes or is marked `RENDER_WITH_OBSERVATION` following its single targeted retry, save the template-safe background as `splash.png` in the task input folder.
