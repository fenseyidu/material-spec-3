# Background Generation

Use this file for every request with a provided reference image before generating template-safe backgrounds.

## Core Rules

- The user-provided image is the reference mother image, not a loose mood board.
- Preserve the reference image's subject identity, category, lighting, color relationship, material, and style unless the user explicitly asks for another strategy. The target resource's written composition rules control the subject's final position, scale, crop, and whitespace; do not preserve the source coordinates when they conflict.
- When the mother image intentionally crops a long, diagonal core product or prop at a canvas edge, preserve that intentional edge-crop character in the generated composition. Keep at least one continuous end of the same core subject extending beyond an output edge; do not shrink or pull the subject fully into frame merely to show it complete. The target resource's title, CTA, crop-buffer, and recognizability requirements remain hard constraints; adapt the cropped edge or endpoint only when needed to satisfy them.
- Do not directly crop, resize, mask, locally clean up, or renderer-fit the original reference image as the final background unless the user explicitly says `直接裁切原图套版`, `不生图，只裁切`, `允许本地兜底`, or equivalent.
- Do not redraw the whole scene, switch to illustration/icon/flat style, or add core subjects, people, products, props, or decorations not present in the reference image. When the reference contains an effective environmental background, do not replace it with a new background.
- Treat a transparent cutout, a flat single-color background, or an isolated product on black/white with no discernible environment as `无有效环境背景`.
- `默认原图` means preserve the original background, composition, lighting, and extension logic as much as possible when an effective environmental background exists. For `无有效环境背景`, the default expression is `极简光影底` unless the user specifies another background strategy.
- `极简光影底` for `无有效环境背景` must retain the product as the sole core subject and derive only subtle, low-saturation ambient gradient, soft light, ground shadow, or weak reflection from the product's visible colors. It must provide environmental support without adding a scene, prop, hard color block, readable text, or competing decoration.
- For a no-title `标准文字套版` source, first generate a `9:16` opening-screen master before renderer. When the source has an effective environmental background, preserve the product/group and its scene logic while naturally extending the existing environment to the target composition. When it has no effective environmental background, use the default `极简光影底` above; do not use the source directly as a renderer background.
- `商品展台底`, `极简光影底`, and `纯色渐变底` are weak background-expression guides. They must not override subject fidelity or scene logic.
- Title, subtitle, CTA, colors, and fonts are for later template rendering only. Do not bake them into the generated background.
- Remove only the original main title, subtitle, and any immediately attached ribbon, color block, or decoration. Preserve all other readable text and its carrier, including product screens, packaging, labels, logos, prices, stickers, and scene text.
- If generation fails or returns no usable generated candidate, stop before crop, local cleanup, `material.json`, renderer, and final delivery. Ask whether to retry generation.

## Prompt Assembly

Build prompts in this order:

```text
【本次可变参数】
主题文案：「【标题】｜【副标题】｜【按钮】」
删除范围：仅原图主标题、副标题及其紧邻的色带、底板或装饰；保留屏幕、包装、产品、标签、Logo、价格、贴纸和场景内其他文字及其载体
标题/副标题颜色：【用户指定色，或按 copy-safety.md 判定的自动色】
文案区承托：【与已判定的深色字/浅色字匹配的中浅色/中深色、低纹理区域】
背景表达：【默认原图 / 商品展台底 / 极简光影底 / 纯色渐变底】
构图裁切：【若母图存在长条斜向核心主体的有意出画，保留至少一个连续端部出画；否则不适用】

【通用固定规则】
Use the rules in this file and `references/shared/copy-safety.md`.

【资源位规则】
Use only the matching `references/resources/<resource>.md`.
The resource file declares the generation canvas or proportion and resource-specific composition rules.
```

When the reference is `无有效环境背景` and the user has not specified a background expression, write `背景表达：极简光影底（从产品可见主色提取低饱和环境光、渐变或柔和地面反射）`. Do not write `默认原图` for this case.

The reference mother image is the only image input. It controls what to draw: content, subject identity, visible products/people, scene logic, and visual style. Use the matching resource file's written rules for placement, scale, crop, whitespace, and generation canvas.
用户参考母图既是唯一图片输入，也控制“画什么”；资源位文件中的文字规则控制“放在哪里”。

Do not add `用途：`, `素材类型：`, or a standalone `参考图：` description to the generation prompt. The attached reference image already supplies that context. Start with the matching resource file's `需求：` sentence; do not duplicate that sentence elsewhere in the prompt.

### First-generation prompt boundary

For a reference-image task, do not restate the mother image as a long `Scene and subject` paragraph. Do not enumerate the reference's environment, lighting, props, decorations, palette, material, or visual style merely because they are visible in the image. The attached mother image already carries those constraints.

Use a short, concrete core-subject label only where a resource rule requires it for layout, for example `黑色立式钢琴与红橙木吉他`. This label identifies what must be measured and placed; it must not expand into a scene inventory or an independent art-direction brief.

Assemble the first-generation prompt in this order:

```text
需求：<matching resource file's required sentence>
构图：<matching resource file's required sentence with the concrete core-subject label>
<matching resource file's safety-zone sentence(s)>
删除范围：仅原图主标题、副标题及其紧邻的色带、底板或装饰；保留屏幕、包装、产品、标签、Logo、价格、贴纸和场景内其他文字及其载体
标题/副标题颜色：<resolved hex color>
文案区承托：<resolved light/dark, low-texture support requirement>
背景表达：<resolved default or user-selected expression>
模板标题、副标题与 CTA 由后续 renderer 呈现。
```

When the conditional edge-crop rule applies, include its Chinese instruction in the assembled generation prompt. It is a composition constraint, not a request to add, remove, or deform the product.

The matching resource file remains the source of truth for composition and safety zones. For standalone `feed` and `popup`, use the compact first-generation prompt in the matching resource file as the complete prompt body. The attached mother image carries the scene identity, and the renderer presents template copy later.

For a request that contains at least two of `feed`, `popup`, and `splash`, or for a no-title `标准文字套版` source, generate one shared `9:16` vertical master using the splash composition as the base. Keep a naturally blended, continuous title/subtitle support area across the full upper area needed by every derived final crop; keep the complete core subject group in the common usable region, with clear space below it for the stricter feed/popup button-lower-edge bands. Do not generate a separate feed or popup candidate. After generation, measure the complete core-subject vertical center in the master and use it to derive each renderer crop.

For `channel`, generate a `1041 x 450` buffered work image with only the original main title/subtitle cleared: use an upper pure-white blank crop buffer, aiming for about `49%` of the image, with a straight full-width hard lower boundary. The exact buffer height is a generation guide rather than a QA target. Render the entire scene only below that boundary; no main subject or key scene structure may protrude above it. Keep the main subject inside the lower-right main-visual area, move it inward from the far-right edge, and keep the lower-left copy-safe area clean for later renderer text. The final renderer does not use the white buffer; it is removed by `prepare-channel-input.py`. When both `channel` and `categoryBanner` are requested, this is the one shared horizontal AI-generation prompt and candidate; derive both resources from it rather than generating a separate Banner image.
