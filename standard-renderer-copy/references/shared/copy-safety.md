# Copy Safety

Use this during prompt assembly and again during Pre-render QA.

## Default Text Handling

Default removal scope is narrow:

```text
remove or weaken only the original main title/subtitle campaign copy;
preserve product, packaging, screen, prop, scene, storefront, and decoration text by default.
```

Do not turn this into full-image text removal, full-logo removal, or full-scene-sign removal.

In every image-generation prompt, explicitly say: remove only the original main title, subtitle, and any immediately attached ribbon, color block, or decoration. Preserve all other readable text and its carrier. Never use wording that asks for whole-image text removal.

## Preserve By Default

Preserve non-conflicting text and its carrier by default:

- prices
- activity slogans
- CTA-like text
- stickers
- labels
- logos
- packaging text
- screen text
- clothing text
- prop text
- storefront, road sign, stage, or scene text
- English slogans
- product model text
- numbers, small marks, texture, and pattern text

Do not blank the product, packaging, screen, prop, or scene structure that carries preserved text.

## Text Color Support

Resolve title/subtitle color before generation. Treat an omitted color as `自动`; do not default it to black.

1. Use an explicit user-supplied title/subtitle color unchanged.
2. For `自动`, judge the title/subtitle safety area only, not the whole image:
   - a bright, low-texture, low-shadow area -> `#111111`;
   - a dark, low-texture, low-glare area -> `#FFFFFF`;
   - a mid-tone, reflective, or visually busy area -> first require an image-derived semi-transparent support area, then choose the darker or lighter color with the clearer contrast.
3. Use one resolved title/subtitle color across a task when every requested resource passes. Use resource-scoped colors only when one shared color cannot pass all copy-safe areas.
4. Record the final resolved hex color in `material.json`. `auto` is a decision mode, never a renderer value.

- 浅色字：需要中深色背景承托，避免高亮、白光、浅色雾面、强反光和复杂亮纹理。
- 深色字：需要中浅色背景承托，避免深色块、暗绿暗蓝、重阴影和复杂暗纹理。
- 文案承托优先从参考图或生成底图的主色/环境色中取色，再做加深或变浅，并以半透明方式融合；不要默认使用纯黑、纯白或与原图无关的硬色块。浅色字用原图色系加深后的中深色承托，深色字用原图色系变浅后的中浅色承托。
- 当参考图属于`无有效环境背景`并默认使用极简光影底时，优先从产品可见主色提取低饱和承托色，并将其弱化为环境光或渐变；不得以纯黑、纯白或高饱和的大面积色块代替文案承托。

## Pre-render Check

PASS when:

- The original main campaign title and adjacent subtitle are removed or weakened.
- The resolved title/subtitle color has a matching clean support area: dark text on a medium-light area, or light text on a medium-dark area.
- Later template title/subtitle/CTA areas are readable; title/subtitle contrast should be at least `4.5:1` where the background can be measured.
- Readability is achieved mainly through composition, spacing, background extension, contrast support, or reduced complexity, not by deleting unrelated text.
- Preserved text carriers remain visually meaningful.

FAIL when:

- Original main title/subtitle still compete with later template copy.
- The title/subtitle safety area does not support the resolved text color, is too reflective, or is too visually busy to read reliably.
- Copy safety is solved by deleting unrelated product, packaging, screen, logo, label, or scene text.
- A preserved text carrier is turned into an empty block and damages realism or category recognition.

On the first failure, do not proceed to renderer; regenerate with a concrete correction. After the single targeted retry, follow `references/shared/visual-qa.md`: render only with a complete `RENDER_WITH_OBSERVATION` record when a remaining issue must be delivered.
