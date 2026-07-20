# Renderer Flow

Use this after Pre-render QA passes or is marked `RENDER_WITH_OBSERVATION` following its single targeted retry. For `channel`, use it after advisory Pre-render QA whether it passes or fails.

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

## No-main-copy Ratio-routed Inputs

Use this path only when the uploaded image has no discernible main title/subtitle, the user has supplied text versions of both, and `python3 scripts/match-resource-size.py --image <image-path>` prints `MATCH`. The direct routes are `3:4` to `feed`, `1:1` to `popup`, `9:16` to `splash`, `1041:225` (about `4.63:1`) to `channel`, and exact `1041:217` to `categoryBanner`. Any matched image that contains either discernible title must not directly route; generate a title-cleaned template-safe background first.

- Ask for title and subtitle before rendering when they are missing; do not use placeholder/default campaign copy.
- Put the original input image in the task folder and map it to the matched resource in `material.json`.
- Run that resource's renderer directly. Do not run AI image generation. For `feed`, `popup`, and `splash`, do not pre-crop locally; the renderer applies its normal cover crop. `channel` and `categoryBanner` use their already-matched horizontal input directly, without additional local cropping.
- If the command prints `NO_MATCH`, do not use this path. Ask for title/subtitle, then generate a template-safe background with only the original main title/subtitle cleared using the matching resource's specified generation canvas or fixed ratio, then render.

## Fixed-ratio Generated Backgrounds

This section applies to standalone AI-generated backgrounds and direct ratio-routed inputs for `feed`, `popup`, and `splash`. A vertical-master combination uses the next section instead.

- Generate `feed` at `3:4`, `popup` at `1:1`, and `splash` at `9:16`.
- The renderer uses its normal centered cover crop to fit these generated backgrounds to the final template dimensions. Do not pre-crop a generated background to the final size.
- During Pre-render QA, assess title, subtitle, and CTA safety against that expected final crop. The documented lower-edge tolerance is for QA acceptance only, not an expansion of the layout. During Render QA, confirm that `feed` and `popup` keep subject content out of the CTA itself.

## Vertical-master Combination: feed / popup / splash

For a request that contains at least two of `feed`, `popup`, and `splash`, generate one `9:16` template-safe vertical master instead of generating separate `3:4`, `1:1`, and `9:16` backgrounds. This mode is limited to those three vertical templates; it does not apply to horizontal resources.

1. Generate one master candidate at `9:16`, with the source title/subtitle cleared and a common, continuous copy-safe area large enough for every requested final crop.
2. Measure the complete core-subject group's vertical center in the master image and record it as normalized `verticalMaster.subjectCenterY` (`0` is the top; `1` is the bottom).
3. Map the same file to every requested vertical resource. The renderer derives each resource's crop position so that the measured master subject center aligns with that resource's canonical main-visual center.
4. Run Pre-render QA separately against each derived final crop. For `feed` and `popup`, continue to enforce the button-lower-edge safety band and the pixel fit gate.

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
- For `feed` or `popup` whose actual primary product is explicitly a 台球杆 / pool cue, set that resource record's `compositionMode` to `poolCueDiagonal`. The renderer then accepts `fitMeasurement.requiredScalePercent: 100` and a retry plan without a scale action; this exemption does not relax title-area or CTA safety checks.
- New task folders must set `qaSchemaVersion` to `4`. Under schema version `4`, `feed`, `popup`, and `splash` require a valid `centeringMeasurement` using the canonical resource-safe bounds; `feed` and `popup` also require a valid pixel-based `fitMeasurement` and `mainVisualFits` check. A `feed` or `popup` record with `targetedRetryCount: 1` additionally requires its `retry-plan.<resource>.json` audit copied into a validated `retryPlan`: the failed-candidate bounds must derive the recorded scale and directions, and the saved prompt must contain every required action. Schema versions `2` and `3` remain rerenderable with their existing centering gate.

Required checks:

| Resource | Check keys |
| --- | --- |
| `channel` | `subjectFidelity`, `copySafeAreaClear`, `cropBufferUsable`, `noBakedTemplateCopy` |
| `categoryBanner` | `subjectFidelity`, `copySafeAreaClear`, `bottomAreaClear`, `noBakedTemplateCopy` |
| `push` | `subjectFidelity`, `copySafeAreaClear`, `noBakedTemplateCopy` |
| `feed`, `popup` | `subjectFidelity`, `mainVisualCentered`, `mainVisualFits` (schema `3`), `copySafeAreaClear`, `bottomAreaClear`, `noBakedTemplateCopy` |
| `splash` | `subjectFidelity`, `mainVisualCentered`, `copySafeAreaClear`, `noBakedTemplateCopy` |

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

Prefer automatic `verticalMaster.subjectCenterY` for a vertical-master combination. Use per-resource `backgroundPosition` only to override that crop deliberately; only use command-line `--background-position` for single-resource test renders.

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
