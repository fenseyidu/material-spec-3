---
name: material-spec-source-style-migration
description: Use when the user needs to generate or batch-render standard operation resource images from template-safe material backgrounds, material.json/request text, or MasterGo-derived templates for channel, categoryBanner, push, feed, popup, splash, and miniProgramShare resources.
---

# Material Spec Skill

Generate standard operation resource PNGs from template-safe material backgrounds.

This skill is the router for the local material-spec workflow. Read only the resource file and shared flow files needed for the current task.

## Use For

- 运营资源位 / 物料规范 / 模板安全物料底图套模板出图.
- Generating one material set: `channel`, `categoryBanner`, `push`, `feed`, `popup`, `splash`, `miniProgramShare`.
- Matching Chinese resource names such as `频道页中通`, `分类筛选 Banner`, `消息页 Push`, `弹窗`, `开屏`, `小程序分享图`.
- Assembling template-safe background prompts from reference-image material requests.
- Updating local renderer specs after the user explicitly asks to read a MasterGo layer.

Do not update Feishu docs, online MasterGo files, or existing production docs unless the user explicitly confirms the exact target.

## When Asked What This Skill Can Do

If the user asks what this skill can do, how to use it, or what prompt to send, answer with:

```text
请按以下模板发起物料任务：

资源位：频道页中通 / 分类筛选 Banner / 消息页 Push / feed / 弹窗 / 开屏 / 小程序分享图
按钮：点击查看
补充要求：可空
```

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
| `miniProgramShare` | `小程序分享图`, `小程序分享`, `分享图` | `references/resources/mini-program-share.md` |

Each resource file declares its layout guide image, generation layout rules, Pre-render QA, and renderer preparation rules. The layout guide path in the resource file is the source of truth for guide selection.

## Shared Flow Files

Read shared files only when the task reaches that stage:

| Stage | Read |
| --- | --- |
| Resource aliases, task folder names, shared-background naming | `references/shared/naming-rules.md` |
| Reference-image material request background generation | `references/shared/background-generation.md` |
| Copy/text migration handling | `references/shared/copy-safety.md` |
| Fast Pre-render QA and Render QA timing | `references/shared/visual-qa.md` |
| Renderer input, `material.json`, render command | `references/shared/renderer-flow.md` |
| Final delivery checks | `references/shared/final-checklist.md` |
| User-requested reports only | `references/shared/reporting-flow.md` |
| MasterGo layer sync | `references/shared/mastergo-sync.md` |

Agent must explicitly state which resource file and shared files were applied before generation/rendering.

## Core Rules

- Resource-specific layout rules live in `references/resources/*.md`.
- Common reference-image, text migration, QA timing, renderer, and delivery rules live in `references/shared/*.md`.
- image gen owns title/subtitle migration and in-image text placement. The bundled renderer owns CTA drawing, rounded corners, dimensions, and technical output validation. Do not duplicate or override renderer implementation details in resource rules.
- For every resource, translate rules into a concise Chinese visual brief before generation. Do not paste rule files, QA checklists, or long negative lists directly into the image-generation prompt.
- Layout guide images stay in `references/layout-guides/`. Do not edit them unless the user explicitly asks.
- Task data folders `material-spec-input/` and `material-spec-output/` must live in the current project/work directory, not inside this skill. The skill may be installed globally and must remain portable across different teammate paths.
- For reference-image material requests, every requested resource must use image gen 生图. Do not silently switch to direct crop, local crop fallback, or renderer-only adaptation unless the user explicitly asks for it.
- Do not use the original reference image itself as renderer input unless the user explicitly says `直接裁切原图套版`, `不生图，只裁切`, `允许本地兜底`, or equivalent.
- Reference-image material requests default to `默认原图`; users do not need to provide a background field unless they want to override that behavior.
- For reference-image material requests, image gen image-to-image generation is required before renderer. If generation fails or returns no usable candidate, stop before crop, cleanup, `material.json`, and renderer.
- For multi-resource reference-image material requests, generate each resource as its own isolated image-to-image call: original reference mother image + only the current resource's declared layout guide. Do not pass all layout guides at once, batch resource prompts in one generation call, or reuse one generated resource as the visual reference for another resource unless a shared-background rule explicitly allows it.
- Before the first local PNG render, check renderer dependencies with `python3 scripts/setup-check.py`. The renderer uses Python/Pillow plus the parent package's shared button font; it does not require Node.js, npm, Chrome, or Playwright.
- Default QA is fast QA: Pre-render QA after generation and Render QA after renderer. Do not generate report artifacts by default. Only read `references/shared/reporting-flow.md` and create reports when the user explicitly asks to generate a report.
- `qa-report.md` and `qa-report.json` are not default required deliverables. Do not require, read, summarize, or deliver them unless the user explicitly asks for a QA report.
- Default targeted retry count is one. Each resource-declared title-group Y anchor is the ideal position. Use the matching resource file's Pre-render QA tolerance when it declares one; otherwise use `ideal Y ± 3% of the relevant canvas height`. Use the title-group top for top-anchor resources and the title-group vertical center for center-anchor resources. Title-group height remains unconstrained. Before any renderer input is prepared, Pre-render QA must record the title-group `top`, `targetY`, and `deltaY`, plus the main-visual `bbox`, `targetCenterX,Y`, and `deltaX,Y`. If any required position cannot be measured, mark QA `BLOCKED`; do not create `material.json` or run renderer. After the one retry, remeasure all required fields, record every remaining deviation as an observation or attention note, and continue to renderer without waiting for confirmation when the candidate and renderer input remain usable.
- Keep measured position and scale deltas in QA notes. Use measured vertical or scale corrections when they provide a reliable target; when a resource declares a percentage-based title anchor, use that target-state wording in the retry prompt while retaining the measurements in QA notes. A resource may declare a coordinated title/main-visual retry: when the title group moves upward, move the complete subject group upward with it. When the main visual is visibly small, enlarge it by `5%-12%` (default about `10%`), preserve its natural aspect ratio, and do not force a tall or narrow subject to fill a wide guide area. Do not describe a scale above `12%` as light. Express main-visual horizontal corrections as an end state rather than a left/right displacement: center the complete subject group in the main-visual area with balanced side whitespace, then keep the other elements unchanged. Keep horizontal pixel/percentage deltas in QA notes only. Remeasure the corrected candidate's title group and main visual before deciding PASS or recording observations.
- Current-task prompt optimization may be specific. Skill-document updates must be generic and should be proposed before writing unless the user explicitly asks to update the skill.

## Production Flow: Reference-Image Material Request

When the user sends a material request with `资源位` and a provided/referenced image, treat it as a production command. `按钮` is optional and defaults to `点击查看`. Background defaults to `默认原图` and does not need to be requested as a field.

1. Parse request fields:
   - `资源位`
   - `按钮`
   - optional extra notes
   Identify the source main title/subtitle from the reference image and migrate them inside the generated image according to `references/shared/copy-safety.md`, unless the user explicitly overrides the copy outside the template.
2. Read `references/shared/naming-rules.md`.
3. Read the matching `references/resources/<resource>.md` for every requested resource.
4. Create a new task-specific folder name from timestamp/theme/resources under the current project/work directory, not inside the skill directory.
5. Read `references/shared/background-generation.md` and `references/shared/copy-safety.md`.
6. Translate the rules into a generation prompt with `references/shared/background-generation.md`:
   - treat the shared rules, copy rules, and resource rules as internal constraints, not prompt text to paste
   - write a short Chinese visual brief that names the current resource, canvas/aspect, composition, concrete reference-image edit actions, migrated copy, and renderer handoff
   - use mostly positive instructions and keep only 1-3 critical negative constraints
   - avoid wording that invites free redesign, such as generic `重生成`; prefer `基于参考图做版式适配和画面延展`
   - every initial image-generation prompt must include this exact sentence: `保持参考图主视觉中人物或者商品不变，只做版式适配；`
   - every initial image-generation prompt must include this exact sentence: `保留图中的字体样式`
   - for initial generation, explicitly label real visual inputs: Image 1 controls what to draw, including content, identity, wording, and visual style; Image 2 controls only spatial layout. Decode Image 2's orange-red title-top line, blue title alignment/flexible-width span, and large orange/red main-visual area in the prompt, and state that guide marks must not appear in the final image
   - if the current generation tool cannot actually attach both initial-generation images as visual inputs, stop and report the limitation instead of pretending file paths in text are image inputs
7. Generate separate template-safe backgrounds per requested resource unless the resource files or naming rules document a shared-background rule. For each resource, provide the original reference mother image again plus only that resource's declared layout guide.
8. If generation fails or produces no usable candidate:
   - do not crop
   - do not create `material.json`
   - do not run renderer
   - ask whether to retry generation
9. After each generated background, read `references/shared/visual-qa.md` and run Pre-render QA using the matching resource file.
10. If Pre-render QA fails:
    - do not crop
    - do not create `material.json`
    - do not run renderer
    - regenerate once with a targeted correction by default
    - first record the required title and main-visual position measurements; any missing measurement is `BLOCKED` and remains a hard stop before renderer
    - for title-group Y or main-visual vertical/scale failures, issue a concise correction toward the guide anchor; for percentage-based title anchors, state the target position rather than a pixel movement; when the title group moves upward, move the subject group upward with it; when the main visual is visibly small, limit its enlargement to `5%-12%` (default about `10%`); for main-visual horizontal centering, describe the centered end state with balanced side whitespace
    - run the full Pre-render QA again, including all required measurements; record every remaining measured deviation as an observation or attention note, then continue to renderer without waiting for confirmation
11. After Pre-render QA completes, read `references/shared/renderer-flow.md`:
    - run the first-use dependency check before renderer
    - install Pillow if missing and permission is available
    - prepare resource-specific renderer inputs
    - for `feed` and `popup`, derive CTA button colors from the generated/reference image unless the user explicitly provided colors outside the template; prioritize button recognizability against the local CTA background before matching title colors
    - create task-specific `material.json` with empty `title` and `subtitle`
    - run renderer; it adds CTA only for templates that declare a button
    - run Render QA
    - allow feed/popup CTA to overlay the main visual; judge the CTA by visibility, clipping, and local contrast, record the overlap as an observation, and continue delivery
12. Read `references/shared/final-checklist.md` before final delivery.
13. Read `references/shared/reporting-flow.md` only when the user explicitly asks to generate a report.
14. Return final paths, Pre-render QA result, Render QA result, and any remaining visual observations.

Correct production path:

```text
reference image
-> per-resource isolated image-to-image generation with only the matching layout guide
-> generated template-safe background candidate with migrated title/subtitle
-> Pre-render QA
-> if FAIL: one targeted retry by default
-> renderer input preparation, with any remaining QA deviations recorded as observations or attention notes
-> material.json with empty title/subtitle
-> renderer adds CTA only where the template declares a button
-> Render QA
-> final checklist
-> final delivery
```

## MasterGo Updates

Only use `references/shared/mastergo-sync.md` when the user explicitly asks to update local specs from a MasterGo URL or layer ID.

Do not push changes back online. Do not update Feishu docs unless the user confirms the exact document and target change.
