---
name: material-spec-skill
description: Route operation-material image requests to the correct local workflow. Use when a user uploads a reference image or asks for a standard operation resource image and needs a choice between preserving the reference image's main title/subtitle visual style or using standardized template copy.
---

# Material Spec Dispatcher

Inspect the uploaded image before creating a task folder, generating an image, reading resource rules, or composing a generation prompt. This file only selects a child skill; never perform production work from this dispatcher.

## Routing

Treat every newly uploaded or newly referenced image as a new routing task. Never reuse a prior `1` or `2` reply, or any prior mode choice, for a different image.

1. Inspect the current image for a discernible main title or subtitle.
   - If neither is discernible and the user has supplied both text title and text subtitle, use `standard-renderer-copy` immediately. Do not ask a style-choice question.
   - If either is discernible, ask exactly:

     ```text
     请选择处理方式：
     1. 原图迁移：保留原图主副标题的字体与视觉样式。
     2. 文字模板：清除图内主副标题后，用标准模板绘制。

     请回复 1 或 2。
     ```

     A reply of `1` applies only to this image and selects `原图迁移`; a reply of `2` applies only to this image and selects `文字模板`. Do not dispatch until the current image has a valid reply.
   - If neither is discernible and either text title or subtitle is missing, ask only for the missing text field. Do not offer original-title migration when no source title exists.
2. If no image is available, ask the user to provide the image before selecting a child skill.

## Dispatch

- For `文字模板`, read [standard-renderer-copy/SKILL.md](standard-renderer-copy/SKILL.md) completely, then follow it as the sole workflow.
- For `原图迁移`, read [source-style-migration/SKILL.md](source-style-migration/SKILL.md) completely, then follow it as the sole workflow.
- After dispatch, do not compose prompts, apply QA, use renderers, or read rules from this file or from the unselected child skill.
- Keep all task folders separate by the selected child skill's documented prefix.

## Shared Dependency

Both child skills read their fonts from `assets/fonts/`. Do not copy, move, or modify those shared fonts during a material task.
