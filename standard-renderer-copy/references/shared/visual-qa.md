# Fast QA Flow

Default mode is fast QA. Do not generate reports by default. Use report artifacts only when the user explicitly asks to generate a report.

## QA Timing

```text
generated candidate
-> Pre-render QA
-> if PASS: prepare renderer input
-> if FAIL: one targeted retry
-> if retry PASS: prepare renderer input
-> if retry FAIL: write RENDER_WITH_OBSERVATION and prepare renderer input
-> renderer
-> Render QA
-> final delivery
```

## Pre-render QA

Run after each generated background and before crop, `material.json`, renderer input, or renderer. For `channel`, only non-severing balance observations are advisory; the horizontal no-severing gate below always blocks renderer.

### Horizontal no-severing gate

For `channel` and `categoryBanner`, a main visual crossing the first-generation white-buffer boundary requires one targeted retry. Replace the white buffer with continuous scene background, visually measure the complete main-visual group as normalized `left,top,right,bottom`, and invoke `prepare-channel-input.py --main-visual-bounds <left,top,right,bottom>`. The script centers the crop on that group's vertical center and never uses pixel white to locate the recovery crop. After that one retry, any remaining crop or balance issue is a `RENDER_WITH_OBSERVATION` record with concrete evidence, then renderer continues.

Before rendering, write the completed result into `material.json.preRenderQA.<resource>` using the required check keys and a concrete `evidence` observation from `references/shared/renderer-flow.md`. This is a required render gate, not a report artifact.

Read:

- `references/shared/copy-safety.md`
- the matching `references/resources/<resource>.md`

PASS only when:

- Subject fidelity is preserved: no unrelated products, people, props, styles, or cross-task elements.
- The candidate follows the matching resource's written composition rules.
- Later template title/subtitle/CTA are not baked into the background.
- Copy-safe areas are readable for the requested text color.
- Main subjects are not unintentionally cut, deformed, replaced, or made commercially weak. A deliberate edge crop is valid only when the mother image uses that composition, the generated product remains continuous and recognizable, and every applicable safety area remains clear.
- The matching resource's CTA, crop-buffer, or other resource-specific rules are satisfied.

### Intentional Edge-Crop Check

When the mother image deliberately sends a long, diagonal core product or prop beyond a canvas edge, treat the resulting edge crop as a required fidelity detail. The generated candidate passes only when at least one continuous end of that same subject exits the final visible frame, the visible product remains recognizable, and the crop does not enter a title/subtitle safe area, CTA lower-edge safety band, or channel copy/buffer area. Do not mark a candidate PASS merely because the full product was pulled inside the canvas.

For `feed`, `popup`, and `splash`, measure the complete in-frame silhouette, including every endpoint that reaches the frame edge; do not omit an edge endpoint to make centering or fit pass. The composition may preserve an edge crop while its in-frame subject group still meets the applicable centering gate.

## Measured Centering Gate: feed, popup, splash only

`mainVisualCentered` applies only to `feed`, `popup`, and `splash`. It does not apply to `channel`, `categoryBanner`, or `push`.

Before deciding this check, inspect the actual final renderer crop and identify the actual core subject group. For a vertical master, first derive the crop from `verticalMaster.subjectCenterY`, unless an explicit `backgroundPosition` overrides it. Exclude title/subtitle/CTA, scenery, light effects, shadows, and non-core decoration. Measure the outer bounds of the core subject group in normalized final-frame coordinates (`0` to `1`) and calculate its center.

For `qaSchemaVersion: 4`, use these canonical main-visual blocks for every centering, fit, title-safety, and retry-direction decision. Do not substitute a copy-box edge, CTA top edge, or raw generation-canvas coordinate.

| Resource | Horizontal bounds | Vertical bounds |
| --- | --- | --- | --- |
| `feed` | `x=0–503` | `y=168–575` in the final `503 x 645` frame |
| `popup` | `x=0–885` | `y=277–912` in the final `885 x 990` frame |
| `splash` | `x=0–1125` | `y=684–1956` in the final `1125 x 1956` frame |

For `qaSchemaVersion: 2` or later, add `centeringMeasurement` to each requested `feed`, `popup`, and `splash` record. The center of `subjectBounds` must be within ±`0.05` of the main-visual block's horizontal center and ±`0.07` of its vertical center. Under schema version `4`, the renderer uses the canonical table above and rejects a `mainVisualCentered` value that disagrees with it.

```json
{
  "coreSubject": "两把吉他组合",
  "subjectBounds": { "left": 0.37, "top": 0.30, "right": 0.63, "bottom": 0.72 },
  "subjectCenter": { "x": 0.50, "y": 0.51 }
}
```

Use the normalized measurement to set `mainVisualCentered`, record the actual direction in `evidence`, and select the matching targeted-regeneration clause when a correction is needed.

## Pixel Subject-Fit Gate: feed and popup only

For `qaSchemaVersion: 4`, `feed` and `popup` also require a pixel-based `fitMeasurement`. Measure the core-subject outer bounds against the expected final renderer crop; do not measure against the raw generated canvas.

### Targeted-regeneration measurement preflight

This is a hard preflight gate for every `feed` or `popup` targeted regeneration. Do not compose or send a targeted-regeneration prompt until all of the following are recorded for the failed candidate:

1. candidate image dimensions;
2. the renderer's actual cover-crop mapping and `backgroundPosition` to the final frame;
3. the full core-subject outer bounds in final-frame pixels;
4. `fitScale`, `shrinkPercent`, and `targetScalePercent` calculated from the QA acceptance bounds;
5. horizontal and vertical displacement relative to the renderer-owned main-visual block.

Measure every protruding edge of every core product: for example, a guitar headstock, a product handle, a stand, a wheel, a base, or a tall accessory. Do not replace the outer bounds with a visual center, the product body alone, or a manually convenient subset. Scenery, light effects, shadows, and non-core decoration remain excluded.

The renderer validates the arithmetic in `material.json`; it cannot determine whether an agent omitted part of the real core subject from a manually observed bound. The agent must therefore visually verify the complete outer bounds before writing the record.

For `qaSchemaVersion: 4`, before sending a `feed` or `popup` retry, write this failed-candidate measurement to `<task-input>/retry-plan.<resource>.json`. It is a required audit record for every retry, including a retry that later passes. After the retry candidate is generated, copy the unchanged object into `preRenderQA.<resource>.retryPlan`. The record must include `sourceImage`, the actual `backgroundPosition`, the matching `coverCrop` mapping, `sourceMeasurement.subjectBoundsPx`, `targetScalePercent`, the ordered `actions`, and the exact `prompt` sent to image generation. Do not paraphrase the saved prompt when calling the image tool.

| Resource | Final frame | Target composition bounds | QA acceptance bounds |
| --- | --- | --- | --- |
| `feed` | `503 x 645` | `x=0–503`, `y=168–575` | `x=0–503`, `y=168–575` |
| `popup` | `885 x 990` | `x=0–885`, `y=277–912` | `x=0–885`, `y=277–912` |

Use the full core-subject group, excluding title/subtitle/CTA, scenery, light effects, shadows, and non-core decoration. Record its pixel bounds and calculate the scale from the original subject size:

```text
fitScale = min(1, safeWidth / subjectWidth, safeHeight / subjectHeight)
shrinkPercent = ceil((1 - fitScale) × 100)
targetScalePercent = 100 - shrinkPercent
```

### Required scale-measurement protocol

For every `feed` or `popup` targeted regeneration, calculate `targetScalePercent` from the expected final renderer frame before writing the prompt. Do not estimate a percentage by looking at the raw generated canvas.

1. Reproduce the renderer's actual cover crop from the candidate's dimensions to the resource's final frame. For a vertical master, use its derived crop position; for an override, use the explicit `backgroundPosition`.
2. Measure the full core-subject outer bounds in that final frame, including every core product and its protruding top, bottom, left, and right edges.
3. Apply the formula above directly to those final-frame pixel bounds. Do not round a visually similar percentage or reuse an earlier candidate's percentage.
4. When scaling is required, write that exact `targetScalePercent` in `缩小至原尺寸的<targetScalePercent>%`.
5. After the one targeted regeneration, repeat steps 1–3 on the new candidate before setting `mainVisualFits`; never assume that the image model applied the requested percentage exactly.

`bottomAreaClear` applies only to the button-lower-edge safety band: `feed y=575–645`, `popup y=912–990`. The CTA button may overlay core subject content, but the button must remain readable.

Use the QA acceptance bounds to calculate `fitScale` and decide whether regeneration is required. The upper bound remains an absolute title/subtitle safety line. The lower bound is the button's lower edge: subject content may sit behind the button but must not enter the safety band beneath it.

Write this record for `feed` and `popup`:

```json
{
  "fitMeasurement": {
    "subjectBoundsPx": { "left": 112, "top": 180, "right": 391, "bottom": 470 },
    "requiredScalePercent": 100
  }
}
```

The renderer derives the fixed safe bounds, verifies the pixel math, and requires `checks.mainVisualFits` to agree. A value below `97` means the candidate needs a targeted regeneration with scaling.

For a vertical master, when deliberately overriding its automatic crop placement because the only issue is mild vertical placement, write one of these values into that resource's `backgroundPosition` before rendering:

- `center 44%`: subject is slightly high; move image content slightly down.
- `center 50%`: default.
- `center 56%`: subject is slightly low; move image content slightly up.

中文口径：

- `center 44%`：主体略高，让画面内容轻微下移。
- `center 50%`：默认值。
- `center 56%`：主体略低，让画面内容轻微上移。

For `feed` and `popup`, the title/subtitle area is hard-avoid. The CTA button may overlay the main visual and must remain readable. Only the button-lower-edge safety band is hard-avoid: `feed y=575–645`; `popup y=912–990`.

对于 `feed` 和 `popup`，标题/副标题区保持硬避让。CTA 按钮可叠加主视觉，但必须清晰可读；仅按钮下边缘安全带保持硬避让：feed `y=575–645`，popup `y=912–990`。

`splash` 当前没有底部操作区；只检查标题/副标题安全区与主视觉居中，不以底部避让作为判定或定向重生条件。

For resources other than `channel`, the first FAIL means:

- Do not crop.
- Do not create `material.json`.
- Do not run renderer.
- Write the concrete visual/copy failure.
- Regenerate once with a targeted correction by default.

After the single targeted retry:

- If it passes, write the final PASS record to `material.json`; the record must state why the candidate now passes.
- If it still fails, write `RENDER_WITH_OBSERVATION` with `targetedRetryCount: 1`, every check result, evidence, and a concise user-facing `observation`; then continue to renderer and include that observation in final delivery.

Do not mark a candidate PASS without checking the applicable resource-specific composition and safety-area rules.

## Targeted Regeneration Prompt

A targeted retry edits the failed candidate image. Inspect that candidate against its matching resource rules, identify the actual core subject, and derive the measured correction from its current displacement. Name the subject specifically, for example `完整的橙色折叠自行车` or `人物与行李箱组合`.

The image-generation prompt contains this single sentence:

```text
<从实际图中判断出的动作>，使<实际核心主体><目的>；主体与其承托物的接触关系、遮挡关系、接触阴影和受力逻辑必须保持；保持商品不变；保持主体组原有构图关系不变：画面中其他元素不变。
```

The sentence contains the correction supported by the current candidate, the actual core subject, the intended result, and the preservation clauses.

For `feed`, `popup`, and `splash`, use the main-visual block only for measurement and QA. Do not copy a raw title-safety interval such as `16%–35%` into a targeted-regeneration prompt. Convert the lower edge of that interval into one concrete top anchor for the core subject group's highest meaningful point.

| Resource | Top anchor | Lower limit for scale calculation |
| --- | --- | --- |
| `feed` | `26%` | button-lower-edge safety band starts at `89.15%` |
| `popup` | `28%` | button-lower-edge safety band starts at `92.12%` |
| `splash` | `35%` | canvas bottom (`100%`) |

The top anchor applies to the actual core subject group's highest meaningful point, including a character's head, hair, face, product body, or tall core prop; exclude light effects, shadows, and non-core decoration. The prompt must name the group as one whole, state that its highest meaningful point should sit at the resource's top anchor, and require horizontal centering. Do not pair this anchor objective with `垂直居中` in the same prompt.

Before sending the prompt, check whether placing the group at the top anchor would push a core part past the lower limit. If so, calculate the needed whole-percent scale from the available height and include `缩小至原尺寸的<百分比>%` before the movement clause. Use the stricter of this result and the existing `feed` / `popup` fit calculation; never enlarge a subject merely to fill the main-visual block.

| QA observation | Required correction clause |
| --- | --- |
| Core subject group is left of the main-visual centerline | `将<实际核心主体>向右移动，使<实际核心主体>在主视觉区内水平居中` |
| Core subject group is right of the main-visual centerline | `将<实际核心主体>向左移动，使<实际核心主体>在主视觉区内水平居中` |
| Core subject group is above the top anchor | `将<实际核心主体>向下移动` |
| Core subject group is below the top anchor | `将<实际核心主体>向上移动` |
| `feed` / `popup` subject content enters the button-lower-edge safety band, or `mainVisualFits` is false | Apply the size-and-position decision sequence below |

For `feed` and `popup`, use this size-and-position decision sequence after judging the actual candidate:

1. Complete the targeted-regeneration measurement preflight and the required scale-measurement protocol: measure `subjectBoundsPx` in the expected final renderer crop and calculate `targetScalePercent` before composing a retry prompt.
2. For `feed` and `popup`, only subject content in the button-lower-edge safety band sets `bottomAreaClear` to `false`; CTA overlap alone does not.
3. Compare the full subject center against the canonical main-visual block center to derive any needed left/right direction. Compare the highest meaningful point against the resource top anchor to derive the needed up/down direction. A subject may need both a horizontal and a vertical direction.
4. When `targetScalePercent` is at least `97`, do not include scale in the prompt. Include only the needed left/right/up/down directions, then append the anchor objective defined above.
5. When the actual primary product is explicitly a 台球杆 / pool cue, write `compositionMode: "poolCueDiagonal"` in its resource QA record. Keep `targetScalePercent` and `fitMeasurement.requiredScalePercent` at `100`, do not add a `scale:*` action or any `缩小至原尺寸` clause, and use only the needed movement directions. When the mother image has an intentional cue edge crop, those movements must retain at least one continuous cue endpoint outside the final frame. This exception is limited to pool cues; visually verify that the real rod silhouette, rather than its overall bounding box, stays out of the title area and the button-lower-edge safety band.
6. For every other product, when `targetScalePercent` is below `97`, include `缩小至原尺寸的<targetScalePercent>%` as the first correction clause in the same prompt, followed by only the needed movement directions and the same anchor objective. Do not state a pixel movement value.
7. Use the stricter scale when either the measured width or height exceeds its safe dimension. Never shrink beyond the calculated whole-percent target merely to clear the button-lower-edge safety band; preserve balanced breathing room and remeasure the retry candidate from its own final renderer crop.
8. Never use `使<实际核心主体>避开 CTA 按钮` or an equivalent CTA-only objective in a targeted-regeneration prompt.

This decision sequence does not apply to `splash`, which currently has no bottom operation area.

Build the sentence from the action supported by the current candidate. Combine horizontal and vertical actions when both measured displacements are present. Only scaling receives a numerical magnitude; movement receives directions only. For `feed`, `popup`, and `splash`, use this form, replacing `<anchor>` with the resource's concrete top anchor:

```text
将<实际核心主体>作为一个整体主体组向<needed direction(s)>移动，使该主体组的最高有效点稳定落在距画面顶部约<anchor>%的位置，并在画面水平方向居中；主体与其承托物的接触关系、遮挡关系、接触阴影和受力逻辑必须保持；保持商品不变；保持主体组原有构图关系不变：画面中其他元素不变。
将<实际核心主体>缩小至原尺寸的<targetScalePercent>%后，作为一个整体主体组向<needed direction(s)>移动，使该主体组的最高有效点稳定落在距画面顶部约<anchor>%的位置，并在画面水平方向居中；主体与其承托物的接触关系、遮挡关系、接触阴影和受力逻辑必须保持；保持商品不变；保持主体组原有构图关系不变：画面中其他元素不变。
```

Use the second form whenever the measured scale is below `97`. The safety interval remains a QA-only rule; do not restate it in the prompt.

For schema version `4`, write this audit shape after any `feed` or `popup` retry. `actions` must be ordered as optional scale, horizontal direction, vertical direction; omit an action that is not needed.

```json
{
  "targetedRetryCount": 1,
  "retryPlan": {
    "sourceImage": { "width": 1254, "height": 1254 },
    "backgroundPosition": "center 50%",
    "coverCrop": { "scale": 0.789474, "scaledWidth": 990, "scaledHeight": 990, "cropLeft": 52, "cropTop": 0 },
    "sourceMeasurement": {
      "subjectBoundsPx": { "left": 325, "top": 180, "right": 835, "bottom": 885 }
    },
    "targetScalePercent": 90,
    "actions": ["scale:90", "left", "down"],
    "prompt": "将两把吉他缩小至原尺寸的90%后，作为一个整体主体组向左、向下移动，使该主体组的最高有效点稳定落在距画面顶部约28%的位置，并在画面水平方向居中；主体与其承托物的接触关系、遮挡关系、接触阴影和受力逻辑必须保持；保持商品不变；保持主体组原有构图关系不变：画面中其他元素不变。"
  }
}
```

For `channel`, write the concrete visual/copy observation, then continue to the channel preprocessor. The preprocessor targets vertical centering of the detected core subject group in the final crop. A channel FAIL can still trigger one targeted regeneration when useful, but it never prevents renderer output.

If image generation returns no usable candidate, Pre-render QA is not reached. Stop and ask whether to retry generation.

## Render QA

Run after renderer completes.

Check:

- output file exists and is nonzero
- expected dimensions
- rounded transparent corners when renderer expects them
- final title/subtitle/CTA are visible and not clipped
- for `feed` and `popup`, the final CTA remains readable; subject content may sit behind the button but must not enter the button-lower-edge safety band

Renderer technical PASS does not override visible copy clipping or obvious visual failure.

Do not require, read, summarize, or deliver `qa-report.md` / `qa-report.json` in default fast mode.
