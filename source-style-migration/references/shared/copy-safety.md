# Copy Safety

Use this during prompt assembly and again during Pre-render QA.

## Default Text Handling

Default handling is in-image title/subtitle migration, not text removal:

```text
identify the original main campaign title and adjacent subtitle in the reference image;
use image gen to redraw only the text content near the resource's ideal title/subtitle Y anchor, within the shared `±3%` vertical range, and at its horizontal alignment anchor;
保留图中的字体样式;
preserve product, packaging, screen, prop, scene, storefront, and decoration text by default.
```

Limit replacement to the original main campaign title/subtitle. Preserve logos, scene signs, product text, and other non-conflicting text. After migration, keep one complete title/subtitle group in the target position.

## Title/Subtitle Migration

When the reference image has an obvious main campaign title and subtitle:

- Treat them as source text to redraw inside the generated image, not as renderer text.
- Single-line title lock: the migrated main title must be rendered as exactly one visual text row for every resource orientation. Even if the reference image splits the same main title across multiple rows, join all source main-title segments into one continuous horizontal line.
- Join all main-title segments into one horizontal row unless the user explicitly requests another treatment.
- If the main title is long, fit it by reducing font size, tightening tracking, or using the full prescribed title width while keeping the entire title readable on one row. Treat the title area's horizontal span as the fit constraint and let the group expand vertically from its anchor. Ask the user before generation only when a readable one-row title is not feasible.
- Keep the main-title baseline parallel to the canvas edge and keep each character upright, flat, and free of perspective.
- Keep the subtitle as a separate subtitle when it exists, unless the user explicitly requests a copy change.
- Preserve the source subtitle wording, font style, color, size hierarchy, weight, and tracking as its natural relative visual role.
- For horizontal resources (`channel`, `categoryBanner`, `push`), place the migrated main title and subtitle in the prescribed title/subtitle area with left alignment.
- For centered card or vertical resources (`feed`, `popup`, `splash`, `miniProgramShare`), place the migrated main title and subtitle in the prescribed title/subtitle area with horizontal center alignment.
- Preserve the source wording and intent; add or rewrite copy only when the user explicitly provides it.
- Preserve title wording and apply this exact instruction during migration: `保留图中的字体样式`. Reset the spatial layout with the target resource's title margin, vertical position, alignment, scale, and title-to-subject gap.
- If OCR/visual reading is uncertain, state the uncertainty and ask the user to confirm the title/subtitle before generation.

If the source title is hard to fit as one row, first reduce size, adjust tracking, use the full prescribed horizontal title width, and preserve readable proportions. Stop and ask the user before generation if a readable one-row title appears impossible.

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

Keep the product, packaging, screen, prop, or scene structure that carries preserved text visually complete.

## Text Color Support

- 浅色字：使用中深色、低反光、低复杂度的背景承托。
- 深色字：使用中浅色、光线平稳、低复杂度的背景承托。
- 多资源位同批生成时，文案承托使用统一策略：优先从参考图或生成底图的主色/环境色中取色，再做加深或变浅并以半透明方式融合。浅色字使用原图色系加深后的中深色承托，深色字使用原图色系变浅后的中浅色承托。

## Pre-render Check

PASS when:

- The original main campaign title and subtitle are migrated within the generated image's allowed title-group Y range and at its horizontal alignment anchor, or explicitly overridden by the user.
- Migrated title/subtitle preserve the source wording, color family, general campaign character, and font style.
- The migrated main title is exactly one visual text row. All source main-title segments are joined into that row, and no main-title phrase is stacked above or below another phrase.
- The main title row is horizontally flat, with a baseline direction parallel to the canvas edge and upright characters.
- Horizontal resources use left-aligned migrated title/subtitle; square and vertical resources use horizontally centered migrated title/subtitle.
- The migrated title group follows the target resource's top or vertical-center anchor and title-to-subject spacing rather than the source image's original coordinates.
- The renderer CTA area supports a visible, unclipped, locally distinguishable button and may contain or overlap the main visual.
- Readability is achieved mainly through composition, spacing, background extension, contrast support, or reduced complexity, not by deleting unrelated text.
- Preserved text carriers remain visually meaningful.

FAIL when:

- Original main title/subtitle remain in the old position and compete with or duplicate the migrated title/subtitle.
- The source main title/subtitle are ignored, misread, removed, or rewritten when the user did not provide replacement copy.
- Migrated title/subtitle do not preserve the source font style or visibly change to an unrelated title treatment when the user did not request a title-design change.
- The migrated main title is split into two or more visual rows when the user did not explicitly approve that exception before generation.
- Any source main-title segment is placed above or below another main-title segment.
- The candidate preserves the reference image's multi-line main-title layout when the user did not explicitly approve it.
- The main title is rotated, skewed, perspective-distorted, arced, waved, or diagonally arranged, even if it remains one row.
- Migrated title/subtitle use the wrong alignment for the resource orientation.
- Copy safety is solved by deleting unrelated product, packaging, screen, logo, label, or scene text.
- A preserved text carrier is turned into an empty block and damages realism or category recognition.

Minor raster variation is an observation when the subtitle remains present, correct, unclipped, readable, and visually faithful to the source. An obvious change to its source typography is a copy failure and may use a targeted correction.

If an objective copy defect fails this check, use `Targeted Retry Routing` in `references/shared/visual-qa.md`. A title Y outside the allowed range may continue only after its one directional retry and must be recorded as a warning; other copy failures must pass before proceeding.
