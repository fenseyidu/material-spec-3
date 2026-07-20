---
name: material-spec-standard-renderer-copy
description: Use when the user needs to generate or batch-render standard operation resource images from template-safe material backgrounds, material.json/request text, or MasterGo-derived templates for channel, categoryBanner, push, feed, popup, and splash resources.
---

# Material Spec Skill

Generate standard operation resource PNGs from template-safe material backgrounds.

This skill is the router for the local material-spec workflow. Read only the resource file and shared flow files needed for the current task.

## Use For

- 运营资源位 / 物料规范 / 模板安全物料底图套模板出图.
- Generating one material set: `channel`, `categoryBanner`, `push`, `feed`, `popup`, `splash`.
- Matching Chinese resource names such as `频道页中通`, `分类筛选 Banner`, `消息页 Push`, `弹窗`, `开屏`.
- Assembling template-safe background prompts from a provided reference image.
- Rendering existing template-safe backgrounds with standardized title/subtitle/CTA templates.
- Updating local renderer specs after the user explicitly asks to read a MasterGo layer.

Do not update Feishu docs, online MasterGo files, or existing production docs unless the user explicitly confirms the exact target.

## When Asked What This Skill Can Do

If the user asks what this skill can do, how to use it, or what prompt to send, answer with:

```text
请按以下任一模板发起物料任务：

资源位：频道页中通 / 分类筛选 Banner / 消息页 Push / feed / 弹窗 / 开屏
标题：
副标题：
标题/副标题颜色：自动（默认）
补充要求：（可空）

已有无标题开屏底图时，使用以下字段：

生成：feed / 弹窗 / 开屏
标题：
副标题：
标题/副标题颜色：自动（默认）
补充要求：（可空）
```

默认使用原图背景、`点击查看` CTA、自动标题/副标题色和模板默认字体。自动色规则按文案安全区决定 `#111111` 或 `#FFFFFF`，并要求底图为选定色提供承托；只有需要覆盖自动判断时，才在“补充要求”中说明文字颜色。`feed`、`popup` 的 CTA 背景与标题同色：深色标题配深色背景和白字，白色标题配白色背景和深色字。

## Resource Router

First normalize requested resource names with `references/shared/naming-rules.md`, then read only the matching resource file:

| Resource | Aliases | Read |
| --- | --- | --- |
| `channel` | `频道页中通`, `中通` | `references/resources/channel.md` |
| `categoryBanner` | `分类筛选 Banner`, `分类筛选Banner`, `分类` | `references/resources/category-banner.md` |
| `push` | `消息页 Push`, `消息页Push`, `Push` | `references/resources/push.md` |
| `feed` | `feed`, `Feed` | `references/resources/feed.md` |
| `popup` | `弹窗` | `references/resources/popup.md` |
| `splash` | `开屏` | `references/resources/splash.md` |

Each resource file declares its generation canvas or proportion, written composition rules, Pre-render QA, and renderer preparation rules.

## Input Routing

When the user provides an image, inspect it before creating a task folder or asking for copy.

1. If the image already contains a discernible main title or subtitle, first determine the campaign copy structure before mapping visible text to `title` and `subtitle`:
   - Treat adjacent large headline blocks in the same main-visual title area as one title candidate even when they use different colors, fonts, or line breaks. For example, `珍品传说` above `皮肤号` becomes the single title `珍品传说皮肤号` when the two blocks form one campaign name.
   - Treat a separately framed information strip, badge, capsule, or descriptor line as the subtitle candidate when it explains the campaign, even if it sits below the headline. Do not infer the subtitle solely from the nearest line break or a color change.
   - Use typography hierarchy, shared title-area placement, visual carriers, and sentence semantics together. A line break or color change alone is not sufficient to split title and subtitle.
   - If the resulting title/subtitle mapping is still ambiguous, stop before generation and ask the user to confirm exactly:

     ```text
     识别结果：
     主标题：<title candidate>
     副标题：<subtitle candidate>

     请确认，或直接改写。
     ```

     Do not ask this confirmation when the mapping is unambiguous.
   - After confirmation when required, or immediately when unambiguous, use the resolved copy as renderer copy. Generate a template-safe background with only the resolved original main title/subtitle and their attached visual carriers removed before renderer; preserve all other in-image text and its carrier.
2. If the image has no discernible main title or subtitle, first classify it before creating a task folder:
   - **底图套版**: use direct rendering only when the image is an already-complete `9:16` opening-screen background with a continuous usable copy-safe area, plus no title/subtitle. Require the user to name one or more of `feed`, `popup`, and `splash`; map that same source image to every requested vertical resource and derive each final crop from its measured `verticalMaster.subjectCenterY`.
   - **标准文字套版**: use this route for a transparent cutout, white/pure-color product image, product group, or ordinary scene image that is not already a complete usable opening-screen background, at any source ratio. Require the user to provide a title, subtitle, and requested vertical resources. Generate one `9:16` title-free opening-screen master, then map it to every requested `feed`, `popup`, and `splash` renderer output. Do not treat a white/transparent/isolated-product image as a direct-render background merely because it is `9:16`.
   - For direct horizontal routes only, run `python3 scripts/match-resource-size.py --image <image-path>`. `1041:225` (about `4.63:1`) routes to `channel`, and the exact `1041:217` routes to `categoryBanner`. Any matched image that contains either discernible title must follow the title-cleanup generation path, not direct rendering. Direct horizontal inputs must match their supported ratio or exact final size. If the user names a resource outside the matched route, ask which route they intend before proceeding.
   - When the source does not meet a direct route and is not a standard-text-template request, ask the user for a resource, title, and subtitle when any are missing; then generate a template-safe background for every requested resource and render the supplied copy.
3. Do not infer campaign copy when the original main title/subtitle are absent. A ratio match removes only the image-generation step, never the need for title/subtitle.

## Shared Flow Files

Read shared files only when the task reaches that stage:

| Stage | Read |
| --- | --- |
| Resource aliases, task folder names, shared-background naming | `references/shared/naming-rules.md` |
| Reference-image background generation | `references/shared/background-generation.md` |
| Copy/text handling | `references/shared/copy-safety.md` |
| Fast Pre-render QA and Render QA timing | `references/shared/visual-qa.md` |
| Renderer input, `material.json`, render command | `references/shared/renderer-flow.md` |
| Final delivery checks | `references/shared/final-checklist.md` |
| User-requested reports only | `references/shared/reporting-flow.md` |
| MasterGo layer sync | `references/shared/mastergo-sync.md` |

Agent must explicitly state which resource file and shared files were applied before generation/rendering.

## Core Rules

- Resource-specific layout rules live in `references/resources/*.md`.
- Common reference-image, text cleanup, QA timing, renderer, and delivery rules live in `references/shared/*.md`.
- The bundled renderer owns final text rendering, CTA drawing, typography, rounded corners, dimensions, and technical output validation. Do not duplicate or override renderer implementation details in resource rules.
- A material request defaults to the original-image background, CTA `点击查看`, automatic title/subtitle color, and template fonts. When the reference has no effective environmental background (for example, a transparent cutout, a flat single-color background, or an isolated product on black/white), default the background expression to `极简光影底`: preserve the product and introduce only subtle, low-saturation light, gradient, or ground reflection drawn from the product's own colors. A user-specified background expression always takes precedence. Resolve automatic title/subtitle color with `references/shared/copy-safety.md` before background generation; write the resolved hex colors to `material.json` before renderer.
- In the no-title branch, `标准文字套版` and `底图套版` are distinct: standard text templating generates a `9:16` opening-screen master from ordinary product/source imagery before renderer; background templating uses an already-complete `9:16` opening-screen background directly. Keep the existing title-bearing standard-text-template flow unchanged.
- Use the Input Routing rules for every uploaded image. The presence of in-image copy controls whether copy is extracted; only a completed no-title `9:16` opening-screen background skips AI image generation for vertical resources.
- For `feed` and `popup`, CTA colors are renderer-fixed from the resolved title color: deep/black title uses the same deep/black button background with white CTA text; white title uses the same white button background with deep CTA text. Do not set `buttonBackground` or `buttonTextColor` in `material.json`, and do not accept a CTA-color override. For these two resources, title color must resolve to the template deep/black (`#111111` or black equivalent) or white (`#FFFFFF`).
- When one request contains at least two of `feed`, `popup`, and `splash`, use one shared `9:16` vertical master instead of separate generated backgrounds. Measure the master core-subject vertical center, write it as `verticalMaster.subjectCenterY` in `material.json`, and let renderer derive each final crop. Run Pre-render QA separately on every requested final crop; an explicit resource `backgroundPosition` is an exception-only override.
- Do not use the original reference image itself as renderer input unless Input Routing identifies it as a completed no-title `9:16` opening-screen background and the user has supplied text title/subtitle, or the user explicitly says `直接裁切原图套版`, `不生图，只裁切`, `允许本地兜底`, or equivalent.
- For a request with a reference image, AI image-to-image generation is required before renderer except on the Input Routing `底图套版` path. If generation fails or returns no usable candidate, stop before crop, cleanup, `material.json`, and renderer.
- Before the first local PNG render, check renderer dependencies with `python3 scripts/setup-check.py`. The renderer uses Python/Pillow and the parent package's shared Alimama ShuHeiTi for main titles plus Alibaba PuHuiTi for subtitles and buttons; it does not require Node.js, npm, Chrome, or Playwright.
- Create every task input folder and output group in the external project workspace, never under the skill directory. The renderer redirects any mistakenly supplied in-skill work path to the skill's parent workspace.
- Default QA is fast QA: Pre-render QA after generation and Render QA after renderer. Do not generate report artifacts by default. Only read `references/shared/reporting-flow.md` and create reports when the user explicitly asks to generate a report.
- `qa-report.md` and `qa-report.json` are not default required deliverables. Do not require, read, summarize, or deliver them unless the user explicitly asks for a QA report.
- `material.json.preRenderQA` is a mandatory render gate, not a report artifact. The renderer requires a complete QA record for every requested resource; non-channel resources require PASS with every required check true, or `RENDER_WITH_OBSERVATION` after exactly one targeted retry with a concrete remaining-issue observation; channel may use its documented `ADVISORY_FAIL` exception with evidence.
- Every new task folder must use `qaSchemaVersion: 4`. For `feed`, `popup`, and `splash` only, `mainVisualCentered` must be supported by the normalized `centeringMeasurement` defined in `references/shared/visual-qa.md`; `feed` and `popup` additionally require the pixel-based `fitMeasurement` and `mainVisualFits` gate. After any `feed` or `popup` targeted retry, include the required `retryPlan` audit record so the measured scale, directions, and exact image-generation prompt are validated together. `channel`, `categoryBanner`, and `push` do not use these gates.
- Default targeted retry count is one. If a usable candidate still fails after that retry, render with `RENDER_WITH_OBSERVATION` and state the concrete remaining issue instead of looping indefinitely; channel retains its documented advisory QA flow.
- A targeted retry is an edit of the failed candidate image. Its image-generation prompt is the single positive correction sentence defined in `references/shared/visual-qa.md`; it names the actual core subject, the measured correction, the intended result, and the two preservation clauses.
- Current-task prompt optimization may be specific. Skill-document updates must be generic and should be proposed before writing unless the user explicitly asks to update the skill.

## Production Flow: Reference Image

When the user provides or references an image and specifies `资源位`, treat it as a production command. No task label is required.

1. Parse request fields:
   - `资源位`
   - `标题`
   - `副标题`
   - optional title/subtitle colors (`自动` when omitted) and supplementary requirements, including a non-default background, CTA copy, or fonts
   - inspect the uploaded image with Input Routing before requesting missing copy or choosing the renderer path; for a no-title standard-text-template source, use the user-supplied title/subtitle and do not infer campaign copy from the image
2. Read `references/shared/naming-rules.md`.
3. Read the matching `references/resources/<resource>.md` for every requested resource.
4. Create a new task-specific folder name from timestamp/theme/resources.
5. Read `references/shared/background-generation.md` and `references/shared/copy-safety.md`.
6. Assemble the generation prompt with:
   - current variables from the request
   - the resolved title/subtitle color strategy and required copy-safe support
   - common background-generation rules
   - common copy-safety rules
   - the matching resource rules
7. Generate separate template-safe backgrounds with only the original main title/subtitle cleared per requested resource, except for documented shared-image groups:
   - when both `channel` and `categoryBanner` are requested, generate one shared horizontal work image from the `channel` rules and use it for both resources; do not generate a second horizontal candidate for `categoryBanner`.
   - when the request contains at least two of `feed`, `popup`, and `splash`, generate one shared `9:16` vertical master from the splash rules; map that same candidate to every requested vertical resource, measure its complete core-subject vertical center, and write `verticalMaster.subjectCenterY` for renderer crop derivation.
   - when the Input Routing result is a no-title `标准文字套版`, generate one shared `9:16` vertical master from the splash rules even when only one vertical resource was requested; map it to every requested vertical resource, measure its complete core-subject vertical center, and write `verticalMaster.subjectCenterY` for renderer crop derivation.
8. On the AI-generation path, if generation fails or produces no usable candidate:
   - do not crop
   - do not create `material.json`
   - do not run renderer
   - ask whether to retry generation
9. On the AI-generation path, after each generated background, read `references/shared/visual-qa.md` and run Pre-render QA using the matching resource file. For a shared `channel` + `categoryBanner` work image, assess the same candidate against both resource files. For a shared vertical master, assess each requested feed/popup/splash result against the renderer crop derived from `verticalMaster.subjectCenterY`, not against the un-cropped master alone.
10. On the AI-generation path, if Pre-render QA fails:
    - for resources other than `channel`, evaluate the expected final crop and CTA placement first. For `feed` and `popup`, the title area and only the documented button-lower-edge safety band remain hard-avoid; the CTA button may overlay the main visual and must remain readable. Other resources follow their matching resource rule. When a candidate needs correction, use that candidate as the retry image input; for `feed` and `popup`, measure scale plus both axes, derive only the necessary directional actions, write them with the exact retry prompt to `retry-plan.<resource>.json`, then send that unchanged prompt. After retry generation, copy the unchanged plan into `retryPlan`. If the retry still needs an observation, write `RENDER_WITH_OBSERVATION` with `targetedRetryCount: 1` and continue to renderer
    - for `channel`, record the concrete observation but continue to `scripts/prepare-channel-input.py`, `material.json`, renderer, and delivery; the channel preprocessor targets vertical centering of the detected core subject group in the final crop. When the candidate is shared with `categoryBanner`, a targeted regeneration edits that one shared candidate and replaces both derived inputs.
11. After Pre-render QA passes, after a permitted `RENDER_WITH_OBSERVATION`, or after an advisory `channel` QA observation, read `references/shared/renderer-flow.md`:
    - run the first-use dependency check before renderer
    - install Pillow if missing and permission is available
    - prepare resource-specific renderer inputs
    - for generated `channel` or `categoryBanner`, run `scripts/prepare-channel-input.py` with the matching `--template` before mapping its image in `material.json`; when both are requested, run it twice against the same shared horizontal work image, once for each template. Direct no-main-copy images that route to either supported horizontal resource bypass it
    - for `feed` and `popup`, resolve the title color to template deep/black or white; renderer derives the matching CTA background/text pair, so do not write CTA color fields to `material.json`
    - write the resolved title/subtitle hex colors to `material.json`; never send literal `auto` to renderer
    - write `qaSchemaVersion: 4` and the final `preRenderQA` record to `material.json`; for a shared vertical master, write its measured `verticalMaster.subjectCenterY` and map the same master filename to every requested vertical resource; for `feed`, `popup`, and `splash`, include the required `centeringMeasurement`; for `feed` and `popup`, also include `fitMeasurement` and `mainVisualFits`, plus `targetedRetryCount: 1` and `retryPlan` (including the actual `backgroundPosition`) when a retry occurred; if the one retry still failed, write `RENDER_WITH_OBSERVATION` with its remaining issue; for advisory channel failures, write its `ADVISORY_FAIL` record with concrete evidence
    - create task-specific `material.json`
    - run renderer
    - run Render QA
12. Read `references/shared/final-checklist.md` before final delivery.
13. Read `references/shared/reporting-flow.md` only when the user explicitly asks to generate a report.
14. Return final paths, Pre-render QA result, Render QA result, and any `RENDER_WITH_OBSERVATION` remaining issue.

Correct production path:

```text
image inspection
-> has title/subtitle: extract copy -> clear only original main title/subtitle -> renderer
-> no original main title/subtitle + completed 9:16 opening-screen background + supplied text copy: direct renderer
-> no original main title/subtitle + ordinary product/source image: generate 9:16 opening-screen master -> renderer
```

## Production Flow: Existing Backgrounds

When the user provides an existing template-safe background and asks only to套版:

1. Inspect each image for a discernible main title/subtitle before treating it as an existing template-safe background. A vertical image can use direct rendering only when it is an already-complete `9:16` opening-screen background with no discernible title/subtitle and a usable continuous copy-safe area, and the user has supplied text versions of both. If the no-title image is a transparent/white/pure-color product source, product group, or ordinary scene rather than a finished opening-screen background, route it through Input Routing's no-title `标准文字套版` generation path. If an image contains either discernible title, do not directly套版; route it through Input Routing's title-cleanup generation path.
2. For an eligible `9:16` vertical background, require the requested output list from `feed`, `popup`, and `splash`, then use that one image as the shared vertical master for all listed outputs. For direct horizontal backgrounds, run `python3 scripts/match-resource-size.py --image <image-path>`; `1041:225` (about `4.63:1`) routes to `channel`, and the exact `1041:217` routes to `categoryBanner`.
3. Read `references/shared/naming-rules.md` and every matching `references/resources/<resource>.md`. For a vertical master, read each requested feed/popup/splash resource rule and derive every final crop from the same image.
4. Read `references/shared/renderer-flow.md`.
5. Run the first-use dependency check before renderer, and install Pillow if missing and permission is available.
6. Resolve automatic title/subtitle color from the actual copy-safe area with `references/shared/copy-safety.md`.
7. Create a new task-specific input folder unless the user explicitly names an existing one to update.
8. Put backgrounds and `material.json` in that folder, using resolved hex colors rather than literal `auto`; for a `9:16` vertical master, map the same filename to every requested vertical resource and write its measured `verticalMaster.subjectCenterY`; write `qaSchemaVersion: 4`, include `centeringMeasurement` for any requested `feed`, `popup`, or `splash`, and include `fitMeasurement` plus `mainVisualFits` for `feed` or `popup`. A `feed` or `popup` retry must also retain `targetedRetryCount: 1` and its `retryPlan`.
9. Run renderer.
10. Run Render QA and `references/shared/final-checklist.md`.
11. Return final paths and Render QA.

## MasterGo Updates

Only use `references/shared/mastergo-sync.md` when the user explicitly asks to update local specs from a MasterGo URL or layer ID.

Do not push changes back online. Do not update Feishu docs unless the user confirms the exact document and target change.

## Repository Releases

Only when publishing a new GitHub version, update `README.md` with current major capabilities and add the release's added, changed, and fixed items to `CHANGELOG.md`. These repository documents are excluded from the clean global-skill export.
