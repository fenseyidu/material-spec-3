# Final Checklist

Use this immediately before delivery.

- Output images are grouped by task/theme in one output folder.
- Previous output groups were not overwritten.
- Expected files exist for requested resources:
  - `channel_1041x225.png`
  - `category_banner_1041x217.png`
  - `push_1035x390.png`
  - `feed_503x645.png`
  - `popup_885x990.png`
  - `splash_1125x1956.png`
- Output dimensions match the renderer report.
- Rounded templates keep transparent corners when applicable.
- The rendered title, subtitle, and CTA are visible and not clipped.
- For `feed` and `popup`, the rendered CTA remains readable. It may overlay the main visual, but the button-lower-edge safety band (`feed y=575–645`; `popup y=912–990`) contains no subject content.
- The AI input image has no later template title/subtitle/CTA baked into it.
- When the mother image deliberately crops a long, diagonal core subject at an edge, the final visible frame retains at least one continuous endpoint outside the frame without violating any resource safety area.
- Template copy comes from `material.json` or parsed request text.
- Every requested resource has a complete `material.json.preRenderQA` record accepted by the renderer gate.
- For `feed`, `popup`, and `splash`, `qaSchemaVersion: 4` and a valid `centeringMeasurement` support the final `mainVisualCentered` result.
- For `feed` and `popup`, `fitMeasurement` records the subject's final-frame pixel bounds, and `mainVisualFits` agrees with the computed `3%` tolerance.
- A `poolCueDiagonal` record is used only when the actual primary product is explicitly a 台球杆 / pool cue; it preserves 100% scale while the title and CTA safety checks remain satisfied.
- After a `feed` or `popup` targeted retry, `retryPlan` records the failed-candidate bounds, exact scale, required directions, and the exact prompt sent to generation; all four agree with the renderer validation.
- For each `RENDER_WITH_OBSERVATION` record, the final delivery explicitly states its remaining issue.
- When both `channel` and `categoryBanner` were requested, confirm they were derived from one shared horizontal AI-generated work image and state: `categoryBanner 由 channel 横图共享生成。`

Do not require report files in default fast mode. Only check or deliver `qa-report.md` / `qa-report.json` when the user explicitly asks to generate a report.
