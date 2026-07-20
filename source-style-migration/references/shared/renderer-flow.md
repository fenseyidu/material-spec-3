# Renderer Flow

Use this after Pre-render QA completes. Continue with every usable candidate, including one with remaining QA deviations; record them as observations or attention notes in the final delivery. Stop only when there is no usable candidate or renderer input cannot be prepared.

## Renderer

The bundled renderer lives in:

```text
assets/material-renderer/
```

Use this Pillow renderer. Do not rebuild it from scratch. It directly composites final PNGs from the generated template-safe backgrounds, draws CTA buttons with the parent package's shared button font, applies rounded corners, and validates output dimensions.

## First-use Dependency Check

Before the first local render, run:

```bash
python3 scripts/setup-check.py
```

The check must verify Python, Pillow, and the parent package's shared renderer button font.

If Pillow is missing, install it before rendering:

```bash
python3 -m pip install Pillow
```

Do not install Node.js, npm, Chrome, or Playwright for this renderer. The Chinese button font is shared at `../assets/fonts/` from this child skill directory.

## Task Input

Put prepared template-safe input images and `material.json` under:

```text
material-spec-input/<task-folder>/
```

This path is relative to the current project/work directory, not the skill directory. Do not store task input/output folders inside the skill, because the skill may be installed globally and shared across teammates with different local paths.

Every reference-image material request with a provided image creates a new task-specific input folder and output group.

The input folder is still required for each task because the renderer needs generated backgrounds plus `material.json`. It is a per-task working folder, not a packaged part of the skill, and it can be recreated for future tasks.

For `channel` and `categoryBanner`, prepare the buffered-horizontal input with the crop optimizer before running the renderer:

```bash
python3 <skill-dir>/scripts/prepare-channel-input.py \
  --template channel \
  --input <generated-channel-candidate.png> \
  --out material-spec-input/<task-folder>/channel.png
```

For `categoryBanner`, use the same optimizer with the category target size:

```bash
python3 <skill-dir>/scripts/prepare-channel-input.py \
  --template categoryBanner \
  --input <generated-categoryBanner-candidate.png> \
  --out material-spec-input/<task-folder>/categoryBanner.png
```

For a candidate that passes with a minor boundary observation, use the optimizer's title-position, real-boundary, and subject-protection scoring, then report the observation.

## Automatic Button Colors

Use this section only for `feed` and `popup`. Derive CTA colors from the reference image and generated renderer inputs unless the user explicitly provides colors outside the template.

- Choose CTA colors by readability first, image palette second. Do not mechanically set the button background to the same color as the title.
- First test whether the CTA will be recognizable as a button against the local background under its renderer placement. The button background must separate clearly from that local region, not only from the button text.
- Prefer sampling stable in-image campaign colors as candidates: title/subtitle colors, price/accent colors, product colors, and material colors that are already visible in the generated input. Use the reference image only as fallback or to keep the palette faithful.
- Treat the dominant in-image campaign text color, especially the main title color, as one candidate, not as the default winner. If it is too close to the CTA placement area's local background, reject it and choose another sampled in-image color.
- Set `buttonTextColor` only after choosing `buttonBackground`; choose readability first, then visual harmony. Do not automatically force the highest-contrast dark/light option when the configured palette color is already readable.
- After `buttonBackground` is selected, test `buttonTextColor` against it with WCAG-style contrast. CTA labels are large, so `>= 3:1` is acceptable when the visual result is clearly readable and more harmonious with the image.
- Candidate text colors should include both dark and light options, for example dark night-sky/text-support colors from the image and light title colors. Pick a readable candidate that fits the image mood; use the highest-contrast fallback only when the configured or sampled palette text is not readable.
- For soft, cute, pastel, warm, or low-contrast images, prefer a softer readable text color such as white/cream on a medium accent button over harsh near-black text, as long as readability remains clear.
- Sample stable text palette colors, not a single pixel. Avoid layout-guide colors, placeholder colors, compression noise, and colors unrelated to the campaign text.
- Do not choose the CTA/button placement area's background color as the button background. The placement area is used for contrast validation, not for primary color selection.
- When the CTA sits on a dark green, dark blue, black, brown, or otherwise visually close area, avoid selecting a similarly dark background even if it matches the title. Pick a contrasting in-image accent such as price/accent color, product trim, wood/metal color, or another sampled color that remains faithful and more recognizable.
- Prefer one task-level color pair when it stays readable across all requested resources. If one pair does not work for every resource, use template-scoped `style` overrides for the failing resources.
- Keep sufficient contrast for the rendered CTA text. If the title-derived button background cannot support readable text with the sampled text palette, keep the closest faithful campaign text color as background and use white or near-black text, whichever is clearer.
- The renderer also applies a final contrast guard: if the configured `buttonTextColor` is too close to `buttonBackground`, it falls back to a readable dark/light text candidate before drawing the CTA. It should not override a harmonious configured text color that already meets large-CTA readability.

## material.json

Prefer explicit mapping. Title/subtitle are already generated inside the image gen background, so keep renderer `title` and `subtitle` empty. The renderer should only add the CTA button when the template has one.

```json
{
  "default": {
    "title": "",
    "subtitle": "",
    "cta": "点击查看"
  },
  "style": {
    "buttonBackground": "#9f1f18",
    "buttonTextColor": "#ffffff"
  },
  "images": {
    "channel": "channel.png",
    "feed": "feed.png",
    "miniProgramShare": "miniProgramShare.png"
  }
}
```

The `style` colors above are examples of auto-derived values. Replace them with the sampled button colors for the current task. If a global pair is readable as text but blends into one resource's CTA placement background, use a template-scoped `style` override for that resource.
Only `feed` and `popup` read `cta`.
Do not put migrated title/subtitle text into `material.json`; it would make the renderer draw duplicate text.

## Render Command

Run from the current project directory:

```bash
python3 <skill-dir>/assets/material-renderer/render.py --all --input-dir=material-spec-input/<task-folder> --output-subdir=<task-folder>
```

Single template:

```bash
python3 <skill-dir>/assets/material-renderer/render.py --template=channel --input-dir=material-spec-input/<task-folder> --output-subdir=<task-folder>
```

The renderer accepts only `material.json.images[template]`, the template's standard input filename, or an explicit `--image`. If the required input is missing, stop and fix it. Shared channel/categoryBanner content must still be prepared or mapped explicitly for each requested template.

## Output

Renderer output should land in:

```text
material-spec-output/<group>/
├── channel_1041x225.png
├── category_banner_1041x217.png
├── push_1035x390.png
├── feed_503x645.png
├── popup_885x990.png
├── splash_1125x1956.png
└── mini_program_share_600x480.png
```

This output path is also relative to the current project/work directory, not the skill directory.

The renderer auto-suffixes output groups when a folder already exists.

Default fast flow does not require or deliver `qa-report.md` / `qa-report.json`. Generate or use report artifacts only when the user explicitly asks for a report.
