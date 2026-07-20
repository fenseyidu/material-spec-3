# Reporting Flow

Reporting is off by default.

Use this only when the user explicitly asks to generate a report or QA report. Do not run this automatically for default fast mode, batch work, production-like work, or repeated failures unless the user asks for reporting.

## Record Attempts

For each meaningful attempt, record:

```text
### Attempt XX：资源位 / 目标

- 生成时间：
- 生图工具：
- 生成目标：
- 输入 task 文件夹：
- 输出文件：
- renderer 输出组：
- Pre-render QA：
- Render QA：
- 发现问题：
- 当前任务提示词优化：
- 是否建议更新 skill 文档：
- 处理结果：
```

Record successful and failed generated candidates when they explain the final decision.

## QA Language

Use separate labels:

```text
Pre-render QA: PASS / FAIL / NOT REACHED
Render QA: PASS / FAIL / NOT RUN
```

Do not write `QA: PASS` when only renderer technical checks passed.

If image generation fails before producing a usable candidate, record:

- `Pre-render QA: NOT REACHED`
- `Render QA: NOT RUN`
- the concrete generation failure
- that crop, local cleanup, `material.json`, and renderer were not run
- the next user-facing question: whether to retry generation

## Skill Update Boundary

Current-task prompt corrections may be specific to the current image.

Skill-document updates must be generic and should be proposed to the user before writing unless the user explicitly asks to update the skill.
