# Renderer Flow

Use this after Pre-render QA passes or is marked `RENDER_WITH_OBSERVATION` following its single targeted retry. For `channel`, `ADVISORY_FAIL` remains available for a non-retry observation.

## Renderer

The bundled renderer lives in:

```text
assets/material-renderer/
```

Use `assets/material-renderer/render.py`. It crops backgrounds, draws the title, subtitle and CTA, applies rounded corners, and validates the final PNG dimensions.

## First-use Dependency Check

Before the first local render, run:

```bash
python3 scripts/setup-check.py
```

The check verifies Python, Pillow, and the parent package's shared Alimama ShuHeiTi for main titles plus Alibaba PuHuiTi for subtitles and buttons. The renderer does not require Node.js, npm, Chrome, or Playwright.

Work directories must stay outside the skill directory. The renderer uses `MATERIAL_SPEC_PROJECT_DIR` or the calling workspace when available; if it is started from inside the skill, it defaults to the skill's parent directory for `material-spec-input/` and `material-spec-output/`. It also redirects any mistakenly supplied in-skill work path to that parent workspace.

If Pillow is missing, install it before rendering:

```bash
python3 -m pip install Pillow
```

## Task Input

Put prepared template-safe input images and `material.json` under:

```text
material-spec-input/<task-folder>/
```

Every request with a provided reference image creates a new task-specific input folder and output group.

For generated `channel` and `categoryBanner` candidates, prepare the input after Pre-render QA and before creating `material.json`:

```bash
python3 <skill-dir>/scripts/prepare-channel-input.py \
  --template channel \
  --input <generated-channel-candidate.png> \
  --out material-spec-input/<task-folder>/channel.png
```

Use `--template categoryBanner` and output `categoryBanner.png` for a generated Banner candidate. Do not send a buffered horizontal work image directly to renderer. When both horizontal resources are requested, pass the same shared AI-generated work image to these two preprocessor calls; do not generate or prepare a second Banner candidate. For `channel`, the preprocessor uses the sustained full-width blank/content boundary rather than the first isolated non-white pixel, and rejects a main visual that protrudes above the boundary. It then targets vertical centering of the detected right-side core subject group in the final crop. A no-main-copy image that routes to `channel` at the supported `1041:225` (about `4.63:1`) ratio, or to `categoryBanner` at the exact `1041:217` size, is already renderer-ready and bypasses the preprocessor.

When visual QA marks a white-buffer crossing, do not render with that first candidate. Its one targeted retry uses continuous-background recovery: visually measure the complete main visual as normalized `left,top,right,bottom`, then run the same preprocessor with `--main-visual-bounds <left,top,right,bottom>`. This uses the measured vertical center to select the crop. If that retry still has a crop or balance issue, write `RENDER_WITH_OBSERVATION` and continue to renderer.

## No-main-copy Ratio-routed Inputs

Use this path only when the uploaded image has no discernible main title/subtitle and the user has supplied text versions of both. A vertical direct input must already be a complete usable `9:16` opening-screen background with a continuous copy-safe area; it is then the vertical master for one or more requested `feed`, `popup`, and `splash` outputs. A transparent/white/pure-color product source, product group, or ordinary scene source is not a direct background and must first follow `标准文字套版` generation. `1041:225` (about `4.63:1`) routes to `channel`, exact `1041:217` routes to `categoryBanner`, and `1035:390` within 1% ratio tolerance routes to `push`. A Push ratio match is renderer-ready without user confirmation. Any matched image that contains either discernible title must not directly route; generate a title-cleaned template-safe background first.

- Ask for title and subtitle before rendering when they are missing; do not use placeholder/default campaign copy.
- Put the original input image in the task folder. For a `9:16` vertical master, map that same filename to every requested `feed`, `popup`, and `splash` resource, measure the complete core-subject vertical center, and write it as `verticalMaster.subjectCenterY` in `material.json`.
- Run the requested renderer templates directly. Do not run AI image generation. For a vertical master, do not pre-crop locally; renderer derives every final crop from `verticalMaster.subjectCenterY`. `channel`, `categoryBanner`, and ratio-matched `push` direct inputs use their uploaded horizontal image directly, without additional local cropping.
- If the command prints `NO_MATCH`, do not use this path. Ask for title/subtitle, then generate a template-safe background using the matching resource's specified generation canvas or fixed ratio, then render.

## Vertical-master Generation: feed / popup / splash

Every AI-generated request containing `feed`, `popup`, or `splash` uses one `9:16` template-safe vertical master from the splash composition. A direct no-main-copy `9:16` input also uses this mode for any requested vertical-resource combination. This mode is limited to those three vertical templates; it does not apply to horizontal resources.

1. Generate one master candidate at `9:16`, with the source title/subtitle cleared and a common, continuous copy-safe area large enough for every requested final crop.
2. Measure the complete core-subject group's vertical center in the master image and record it as normalized `verticalMaster.subjectCenterY` (`0` is the top; `1` is the bottom).
3. Map the same file to every requested vertical resource. The renderer derives each resource's crop position so that the measured master subject center aligns with that resource's canonical main-visual center.
4. Run Pre-render QA separately against each derived final crop. For `feed` and `popup`, continue to enforce the button-lower-edge safety band and the pixel fit gate.

When `material.json.referenceEdgeCrops` is declared, renderer does not outpaint, extend, or locally fabricate the off-canvas product. It derives the normal cover crop, then requires each requested resource's QA record to confirm the same declared exit edge(s), exit direction, continuity, and relative occlusion. `verticalMaster.subjectCenterY` and any `backgroundPosition` override may improve vertical placement only if the resulting crop still passes that contract; they must not be used to pull a declared exited subject back inside the final frame.

```json
{
  "verticalMaster": { "subjectCenterY": 0.675 },
  "images": {
    "feed": "vertical-master.png",
    "popup": "vertical-master.png",
    "splash": "vertical-master.png"
  }
}
```

`backgroundPosition` remains an explicit per-resource override. When it is present, the renderer uses it instead of `verticalMaster.subjectCenterY`. Use an override only when QA identifies a justified crop adjustment, and record that actual crop position in a `feed` or `popup` `retryPlan.backgroundPosition` when a targeted retry occurs.

## material.json

Before renderer, resolve title/subtitle `自动` to a hex color using the actual copy-safe area and `references/shared/copy-safety.md`. Write the resolved value; `render.py` accepts colors such as `#111111` and `#FFFFFF`, not literal `自动`.

### Mandatory Pre-render QA Gate

The renderer refuses to create PNGs until every requested resource has a complete `preRenderQA` record in `material.json`.

- For all resources other than `channel`, `status` must be `PASS`, or `RENDER_WITH_OBSERVATION` after exactly one targeted retry.
- `RENDER_WITH_OBSERVATION` requires `targetedRetryCount: 1`, at least one failed required check, and a concrete `observation`. The renderer prints that observation, and final delivery must repeat it.
- `channel` preserves its advisory workflow: `status` may be `PASS` or `ADVISORY_FAIL`. An `ADVISORY_FAIL` still requires every check key and a concrete `evidence` observation.
- A missing record, missing check, failed check under `PASS`, empty evidence, or an invalid retry/observation record stops rendering before any output group is created.
- When top-level `referenceEdgeCrops` is declared, every requested resource must include `referenceEdgeCropsPreserved` and a `referenceEdgeCropMeasurement`. `PASS` requires `referenceEdgeCropsPreserved: true` plus an exact match for every declared subject's exit edge(s), direction, continuity, and relative occlusion. After exactly one targeted retry, `RENDER_WITH_OBSERVATION` may set the check to `false`, record the actual observed exit state, and state the remaining edge-crop issue.
- `compositionMode: "poolCueRightBiased"` is the only 台球杆-specific QA exception. It is limited to feed, popup, and splash where the approved composition requires a 台球杆从右上自然出画. It replaces `mainVisualCentered` with `poolCueRightBiased`, validated from `poolCueMeasurement`. Only `feed` or `popup` may additionally set their own `poolCueTitleGapAllowance: true`; this permits the cue head in upper non-text space only when `poolCueTitleGapClear` is true. It never relaxes text-glyph readability, the CTA lower-edge safety band, product fidelity, or the edge-crop contract.
- New task folders must set `qaSchemaVersion` to `4`. Under schema version `4`, `feed`, `popup`, and `splash` require a valid `centeringMeasurement` using the canonical resource-safe bounds, except `poolCueRightBiased`, which requires `poolCueMeasurement`; `feed` and `popup` also require a valid pixel-based `fitMeasurement` and `mainVisualFits` check in either mode. A `feed` or `popup` record with `targetedRetryCount: 1` additionally requires its `retry-plan.<resource>.json` audit copied into a validated `retryPlan`: the failed-candidate bounds must derive the recorded scale and directions, and the saved prompt must contain every required action. Schema versions `2` and `3` remain rerenderable with their existing centering gate.

Required checks:

| Resource | Check keys |
| --- | --- |
| `channel` | `subjectFidelity`, `copySafeAreaClear`, `cropBufferUsable`, `noBakedTemplateCopy` |
| `categoryBanner` | `subjectFidelity`, `copySafeAreaClear`, `bottomAreaClear`, `noBakedTemplateCopy` |
| `push` | `subjectFidelity`, `copySafeAreaClear`, `noBakedTemplateCopy` |
| `feed`, `popup` | `subjectFidelity`, `mainVisualCentered`, `mainVisualFits` (schema `3`), `copySafeAreaClear`, `bottomAreaClear`, `noBakedTemplateCopy`, plus `referenceEdgeCropsPreserved` when `referenceEdgeCrops` is declared. Under `poolCueRightBiased`, replace only `mainVisualCentered` with `poolCueRightBiased`; when that resource explicitly enables `poolCueTitleGapAllowance`, also require `poolCueTitleGapClear`. |
| `splash` | `subjectFidelity`, `mainVisualCentered`, `copySafeAreaClear`, `noBakedTemplateCopy`, plus `referenceEdgeCropsPreserved` when `referenceEdgeCrops` is declared. Under `poolCueRightBiased`, replace only `mainVisualCentered` with `poolCueRightBiased`. |

Example:

```json
{
  "qaSchemaVersion": 4,
  "preRenderQA": {
    "feed": {
      "status": "PASS",
      "checks": {
        "subjectFidelity": true,
        "mainVisualCentered": true,
        "mainVisualFits": true,
        "copySafeAreaClear": true,
        "bottomAreaClear": true,
        "noBakedTemplateCopy": true
      },
      "centeringMeasurement": {
        "coreSubject": "完整的橙色折叠自行车",
        "subjectBounds": { "left": 0.33, "top": 0.30, "right": 0.67, "bottom": 0.72 },
        "subjectCenter": { "x": 0.50, "y": 0.51 }
      },
      "fitMeasurement": {
        "subjectBoundsPx": { "left": 166, "top": 180, "right": 337, "bottom": 470 },
        "requiredScalePercent": 100
      },
      "evidence": "主体组与主视觉区中心对齐；按钮可叠加主体，按钮下边缘安全带无主体内容。"
    }
  }
}
```

If the single targeted retry still fails:

```json
{
  "qaSchemaVersion": 2,
  "preRenderQA": {
    "feed": {
      "status": "RENDER_WITH_OBSERVATION",
      "targetedRetryCount": 1,
      "checks": {
        "subjectFidelity": true,
        "mainVisualCentered": false,
        "mainVisualFits": false,
        "copySafeAreaClear": true,
        "bottomAreaClear": true,
        "noBakedTemplateCopy": true
      },
      "centeringMeasurement": {
        "coreSubject": "完整的橙色折叠自行车",
        "subjectBounds": { "left": 0.54, "top": 0.30, "right": 0.90, "bottom": 0.72 },
        "subjectCenter": { "x": 0.72, "y": 0.51 }
      },
      "fitMeasurement": {
        "subjectBoundsPx": { "left": 272, "top": 194, "right": 453, "bottom": 548 },
        "requiredScalePercent": 87
      },
      "evidence": "第二次候选图仍偏右，其他检查通过。",
      "observation": "主体组仍偏右，未达到主视觉居中要求。"
    }
  }
}
```

Prefer explicit mapping:

```json
{
  "default": {
    "title": "国庆出游季",
    "subtitle": "出游装备限时特惠",
    "cta": "点击查看"
  },
  "style": {
    "titleColor": "#111111",
    "subtitleColor": "#111111"
  },
  "images": {
    "channel": "channel.png",
    "feed": "feed.png"
  }
}
```

If a requested resource template does not display CTA, still store `cta` in `material.json` and mention this in delivery notes.

## CTA Colors

Apply this section only to `feed` and `popup`. The renderer derives CTA colors from the final `titleColor`; do not write `buttonBackground` or `buttonTextColor` to `material.json` and do not accept CTA-color overrides.

- A deep/black title (`#111111`, `#000000`, or equivalent shorthand) produces the same deep/black button background and white CTA text.
- A white title (`#FFFFFF` or shorthand) produces the same white button background and deep `#111111` CTA text.
- The resolved title color for these resources must be deep/black or white. Do not use a colored title, because it would violate the black/white CTA rule.

Optional per-resource crop-position override:

```json
{
  "images": {
    "feed": "feed.png",
    "popup": "popup.png",
    "splash": "splash.png"
  },
  "feed": {
    "backgroundPosition": "center 56%"
  },
  "popup": {
    "backgroundPosition": "center 44%"
  },
  "splash": {
    "backgroundPosition": "center 50%"
  }
}
```

Prefer automatic `verticalMaster.subjectCenterY` for every vertical master. Use per-resource `backgroundPosition` only to override that crop deliberately; only use command-line `--background-position` for single-resource test renders.

竖版母图组合优先使用 `verticalMaster.subjectCenterY` 自动裁切；只有明确需要覆盖时，才按资源位在 `material.json` 写 `backgroundPosition`。只有单资源位测试渲染时，才使用命令行 `--background-position`。

## Render Command

Run from the current project directory:

```bash
python3 <skill-dir>/assets/material-renderer/render.py --all --input-dir=material-spec-input/<task-folder> --output-subdir=<task-folder>
```

Single template:

```bash
python3 <skill-dir>/assets/material-renderer/render.py --template=channel --input-dir=material-spec-input/<task-folder> --output-subdir=<task-folder>
```

Use `verticalMaster.subjectCenterY` to derive vertical-master crop placement, or `backgroundPosition` in `material.json` for a per-resource override. The renderer supports `left`/`center`/`right`, `top`/`center`/`bottom`, and vertical percentages such as `center 56%`.

## Output

Renderer output should land in:

```text
material-spec-output/<group>/
├── channel_1041x225.png
├── category_banner_1041x217.png
├── push_1035x390.png
├── feed_503x645.png
├── popup_885x990.png
└── splash_1125x1956.png
```

The renderer auto-suffixes output groups when a folder already exists.

Default fast flow does not require or deliver `qa-report.md` / `qa-report.json`. Generate or use report artifacts only when the user explicitly asks for a report.
