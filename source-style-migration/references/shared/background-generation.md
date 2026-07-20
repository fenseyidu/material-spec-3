# Background Generation

Use this file for every reference-image material request before generating template-safe backgrounds.

## Core Rules

- The user-provided image is the reference mother image, not a loose mood board.
- Treat the reference mother image as the visual-content source of truth, not as a spatial-layout source and not as a set of style keywords to reinterpret.
- Preserve visible source identity and content by referring back to the attached reference image itself. Use the target resource layout for title margin, element coordinates, subject scale, crop, and spacing. Describe the visual style through the reference image itself so the result keeps the same effects, props, subjects, typography system, and visual theme.
- Regenerate every requested resource with image gen from the reference mother image.
- Generate each requested resource as an isolated image-to-image unit: one generation call uses the reference mother image plus that resource's matching layout guide image. Repeat this isolated setup for every resource.
- For every initial generation call, explicitly label the visual inputs and divide their authority precisely: Image 1 controls content, subject identity, wording, and visual style; Image 2 controls only spatial layout. Decode Image 2's visible guide marks in the prompt: the bright orange-red horizontal line marks the title group's ideal top anchor, blue marks title/subtitle horizontal alignment and flexible width rather than a fixed-height box, and the large orange/red rectangle marks the main-visual placement area. State that guide colors and shapes are invisible placement references and must not appear in the final image.
- For non-channel resources, use the layout guide only as an invisible placement reference. Generate one continuous background extended from the reference image; place migrated title/subtitle directly on that extended background and keep the main subject in the guide-defined visual area. Treat the resource-declared title-group Y anchor as the ideal position, with an acceptable vertical range of `ideal Y ± 3% of the relevant canvas height`. When the guide has a bright orange-red horizontal line, its center is the ideal title-top anchor; use the blue title region as the horizontal alignment and flexible expansion span, not a fixed-height box.
- For `channel`, follow `references/resources/channel.md`: render only Image 2's lower effective material area and keep the upper white crop buffer empty with a straight horizontal hard edge.
- Every initial generation prompt must include this exact sentence: `保持参考图主视觉中人物或者商品不变，只做版式适配；`
- Immediately clarify that sentence in every initial generation prompt: `这里的“不变”仅指主体身份、外观、数量和关键细节；主体位置、大小、裁切、标题上边距和画面留白必须按当前资源位 layout guide 重新排布。`
- Every initial generation prompt must include this exact sentence: `保留图中的字体样式`
- Start each resource from the original reference mother image, except where a resource file or naming rule explicitly documents a shared-background rule. For a same-resource targeted correction, use the current candidate as the edit target and the current guide as internal spatial authority; include the original mother only as a supporting identity reference when useful.
- Use an image-gen result as the final background. Use direct crop, resize, mask, local cleanup, or renderer fitting of the original reference only when the user explicitly says `直接裁切原图套版`, `不生图，只裁切`, `允许本地兜底`, or equivalent.
- In prompt text, describe the intended end state: fit the reference image into the requested layout, place and scale visible source subjects inside the guide areas, migrate campaign copy, and account for later renderer elements. For feed/popup, keep the main visual composition strong and allow the later CTA to overlay it.
- Keep the same scene logic, visual category, core subjects, people, products, props, background content, and decorations as the reference image.
- Use image-to-image generation internally, but avoid prompt wording that suggests free redesign. Prefer language such as `视觉内容以参考图为准，空间排版以当前资源位 layout guide 为准`.
- Default background handling is `默认原图`: use the original reference image as the source of background content and visual identity, then rebuild the composition with the target resource's title anchor, subject position, subject scale, crop, and whitespace as the spatial defaults.
- If the user explicitly requests another background expression, treat it as a weak guide. It must not override subject fidelity or scene logic.
- The main title and subtitle are generated into the image by image gen. The renderer does not add either text element.
- Preserve and redraw the reference image's main title and subtitle into the resource's layout-defined title/subtitle area.
- In every image-generation prompt, call the subtitle text `副标题`. Preserve its source font style, size hierarchy, weight, tracking, color, and relative visual role; do not impose a fixed subtitle-to-main-title ratio. Keep it readable without changing those source typography characteristics.
- The reference mother image controls the subtitle wording and typography as well as the color family, subject, and scene. If both text rows do not fit, first rebalance the composition or scale the whole title group proportionally; do not change only the subtitle's typography.
- For prompt text, say `替换/迁移原主标题位置的文字，并保留图中的字体样式`.
- For horizontal resources (`channel`, `categoryBanner`, `push`), redraw migrated title/subtitle left-aligned.
- For centered card or vertical resources (`feed`, `popup`, `splash`, `miniProgramShare`), redraw migrated title/subtitle horizontally centered.
- Single-line title lock: the migrated main title must be rendered as exactly one visual text row for every resource orientation. Even if the reference image splits the same main title across multiple rows, join all source main-title segments into one continuous horizontal line.
- Place every main-title segment on the same horizontal baseline as one continuous row unless the user explicitly asks for another treatment.
- If the main title is long, first reduce font size, tighten tracking, preserve readable proportions, or use the full blue flexible title span, but keep the entire main title on one row.
- The migrated main title must be horizontal and flat for every resource orientation: keep the text baseline direction parallel to the canvas edge, keep characters upright, and do not use rotation, skew, perspective, arc, wave, or diagonal title layout.
- For `feed` and `popup`, the renderer adds the CTA later. Keep every generated background free of CTA buttons.
- If generation fails or returns no usable generated candidate, stop before crop, local cleanup, `material.json`, renderer, and final delivery. Ask whether to retry generation.

## Spatial Layout Authority

Apply spatial instructions in this order:

1. The user's current explicit spatial request.
2. The target resource file and its matching layout guide.
3. The reference mother's original composition only for choices that the target layout does not specify.

Image 1 controls subject identity, scene content, wording, color family, and visual character. Image 2 controls only spatial layout: title anchor and alignment, subject center and scale, crop, title-to-subject gap, resource-specific renderer placement, and whitespace. Use Image 2 for spatial relationships while keeping Image 1's content and visual style. Feed/popup CTA may overlay the main visual.

## Targeted Retry Prompt

For a same-resource targeted correction, keep measured layout and QA rules as internal control data. Use the current candidate as the edit target and keep the current guide as internal spatial authority. Attach the guide only when a complex correction needs it as a visual input.

Write one short Chinese sentence that states the desired end state and keeps the other elements unchanged. Use measured pixel movement for reliable vertical corrections such as title Y, unless the current resource declares a percentage-based title anchor; in that case, state the target position and keep the measured delta in QA notes only. When the title group moves upward, move the complete subject group upward with it. When the main visual is visibly small, enlarge it by `5%-12%` (default about `10%`) while preserving its natural aspect ratio; do not force a tall or narrow subject to fill a wide guide area. For main-visual horizontal centering, describe the centered result with balanced side whitespace and keep horizontal pixel/percentage deltas in QA notes only.

Canonical horizontal-centering example:

```text
将主视觉主体组在画面中水平居中，左右留白相等，其他画面元素保持不变。
```

Replace `主视觉主体组` with the concrete subject when useful, such as `两把吉他` or `人物与商品组合`.

Measured vertical-correction example:

```text
将主标题和副标题作为整体上移约 99px，其他画面元素保持不变。
```

Percentage-anchor example:

```text
将主标题和副标题作为整体移动，使标题组顶部对齐画布顶部约 10% 的位置，其他画面元素保持不变。
```

Coordinated title/main-visual example, only when the resource declares it and QA confirms the condition:

```text
将主标题和副标题作为整体上移，使标题组顶部对齐画布顶部约 10% 的位置；同时将完整主视觉主体组相应上移；若主体偏小，放大约 10%（不得超过 12%），保持主体自然比例、水平居中、左右留白均衡，其他画面元素保持不变。
```

Limit the retry prompt to the action and the invariant. Keep image labels, guide explanations, anchor coordinates, bounding boxes, formulas, canvas percentages, copy restatements, and long preservation lists in the QA notes rather than the prompt.

## Prompt Translation

Translate this file, `copy-safety.md`, resource rules, QA criteria, and renderer instructions into a concise task-specific visual brief.

Before generation, translate the applicable rules into a concise Chinese visual brief for the current resource. The brief should be easy for an image model to follow:

- Start with the resource name and intended canvas/aspect.
- Describe the composition in visual terms, using the resource guide to define the invisible title anchor, main-visual anchor, resource-specific CTA/crop safety, and whitespace relationships. Decode the guide marks explicitly: the bright orange-red horizontal line's center is the title group's ideal top anchor; blue is the title/subtitle horizontal alignment and flexible-width span, not a fixed-height title box; the large orange/red rectangle is the main-visual placement area. State that these guide marks must remain invisible in the final image.
- If the resource file declares approximate percentage ranges for subject, CTA, crop buffers, or safe areas, translate those ranges into explicit prompt constraints. State the resource-declared `titleTopAnchor` or vertical-center Y as the ideal positional target and keep the title group within `ideal Y ± 3%` of the relevant canvas height. Use the blue title region only for horizontal alignment and flexible width; let the title group expand vertically from its top or around its center.
- State only the concrete reference subjects that must be placed when needed. Explicitly say that their identity and appearance come from Image 1 while their position, scale, and crop come from Image 2. Avoid mood, atmosphere, art-direction, lighting, color-system, texture, or typography-style adjectives that are not required by the user.
- State the main title and `副标题` text, placement, alignment, replacement/migration action, the exact sentence `保留图中的字体样式`, preservation of the source subtitle typography, and the single-line title lock: the main title must be one visual row, any source multi-row title must be joined into one row, and the title must be horizontal, flat, and free of perspective.
- State the renderer handoff only when the current resource uses CTA.
- Keep the prompt positive and describe the intended final image. Reserve at most 1-3 negative constraints for hard failures such as a baked CTA or visible guide/template structure. Express copy requirements positively: keep one migrated title/subtitle group and render the main title as one horizontal row.

Back the prompt with real visual inputs: attach both the reference mother image and the current layout guide. Treat local file paths in prompt text as metadata rather than visual input. If both images cannot be attached, stop and report that limitation.

## Prompt Brief Shape

Build the final image prompt in this order:

```text
请基于参考图制作一张「【资源位中文名】」物料背景，画幅/工作图比例为【尺寸或比例】。

视觉输入：
Image 1 = 参考母图，控制画面内容、主体身份、文字内容和视觉风格，不控制原图中的空间排布。
Image 2 = 当前资源位 layout guide，仅控制空间排布：橙红色横线中心表示标题组的理想顶部位置；蓝色区域表示标题和副标题的横向对齐范围与可延展宽度，不限制标题组高度；大块红色或橙色区域表示主视觉放置区域。标题和主体的位置、缩放、裁切及资源位声明的留白以 Image 2 为准，画面内容、主体身份、文字内容和视觉风格仍以 Image 1 为准。guide 中的色块和线条保持为不可见的定位参考。

构图：
【用 2-5 句把当前资源位规则翻译成自然视觉语言。说明标题组必须对齐的顶部 Y 或垂直中心 Y、横向锚点和主视觉区；仅当当前资源文件声明时，才说明 CTA 预留区、裁切缓冲区或其他留白要求。标题组高度不受蓝色区域限制，可以从固定顶部向下延展，或围绕固定垂直中心扩展。除 channel 外，成品是一张由参考母图自然延展出的完整背景；channel 只渲染 guide 下方有效区域。标题直接落在对应背景上，主视觉完整放入主视觉区。】

参考图处理：
以 Image 1 为准做版式适配；需要点名时只点名具体可见主体，例如主要人物、商品或场景元素。
保持参考图主视觉中人物或者商品不变，只做版式适配；
这里的“不变”仅指主体身份、外观、数量和关键细节；主体位置、大小、裁切、标题上边距和画面留白按当前资源位 layout guide 重新排布。
直接以参考图的可见内容和视觉风格为准进行版式适配。

图内文案：
主标题：「【主标题】」
副标题：「【副标题】」
保留图中的字体样式
【说明左对齐或居中、替换/迁移旧标题、可读性和单行标题锁定：「【副标题】」作为副标题，保留参考图中的字体样式、字号层级、字重、字距、颜色和相对视觉角色。若标题区空间不足，优先调整构图或等比缩放整个标题组，保持副标题的排版特征和缩略预览可读性。主标题合并为一行水平横排，文字基线与画布水平边平行，字符保持直立、平面和无透视。迁移完成后，画面中只保留一组完整的主标题和副标题。】

按钮（仅 feed / popup）：
「【按钮】」由后续 renderer 添加。本次生成背景和图内标题/副标题；主视觉按 guide 保持完整有力，后续 CTA 可以叠加在主视觉上。

其他资源省略按钮段落。

关键约束：
【只在必要时写 1-3 条硬约束，例如背景中不提前画按钮、成品中不出现可见 guide 色块或模板框架。】
```

For initial generation and subject-fidelity restarts, pass the declared layout guide to the image-generation tool as a structural visual input. Treat a path mentioned in prompt text as metadata only. Same-resource targeted corrections follow `Targeted Retry Prompt`.
首次生成和主体保真重启时，把资源位声明的 layout guide 作为结构视觉输入传给生图工具；prompt 中的路径只作为元数据。同资源定向修正遵循 `Targeted Retry Prompt`。

For multi-resource tasks, repeat the visual-input setup separately for each resource. Example: provide the reference mother image with `feed-layout-guide.png` for `feed`, then provide the same mother image with `popup-layout-guide.png` for `popup` in a separate call.
多资源位任务逐资源位重新建立视觉输入。例如：生成 `feed` 时提供参考母图和 `feed-layout-guide.png`；生成 `popup` 时在独立调用中再次提供同一张参考母图和 `popup-layout-guide.png`。

The reference mother image controls "what to draw"; the layout guide controls "where to place it" and overrides the source image's spatial relationships.
用户参考母图控制“画什么”；layout guide 控制“放在哪里”，并优先于原图的标题上边距、主体位置、缩放、裁切和留白关系。

Layout guide color semantics:

- When present, a bright orange-red horizontal line marks the title group's ideal top anchor. Use the line center as the ideal title-top Y; its thickness is not a title-area height.
- Blue marks the title/subtitle horizontal alignment and flexible expansion span. Its vertical height is not a crop box, fit box, or PASS/FAIL boundary; judge the resource file's declared title-top or vertical-center Y using its Pre-render QA tolerance.
- A large orange/red rectangle marks the main visual placement area.
- Keep guide colors and shapes invisible in the final image.
