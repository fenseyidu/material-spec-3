# Fast QA Flow

Default mode is fast QA. Do not generate reports by default. Use report artifacts only when the user explicitly asks to generate a report.

## QA Timing

```text
generated candidate
-> Pre-render QA
-> if PASS: prepare renderer input
-> if FAIL: one targeted retry by default
-> run full Pre-render QA again
-> record any remaining deviation as an observation or attention note
-> renderer
-> Render QA
-> if Render QA FAILS: apply the matching correction and rerun Render QA
-> final delivery
```

## Pre-render QA

Run after each generated background and before crop, `material.json`, renderer input, or renderer.

## Cue-Only Product Exception (Source-Style Migration Only)

Apply this exception only inside the `source-style-migration` workflow. A qualifying cue-only product reference has billiard cue(s) as its only commercial subject and shows no person, hand, or arm holding a cue. Incidental scene props such as billiard balls, a billiard table, chalk, books, or a desktop do not disqualify it.

- Run the full Pre-render QA exactly as normal, including every required position measurement and all copy, template, and CTA checks.
- If the candidate is usable and not `BLOCKED`, never perform a QA-triggered targeted correction, restart, or any other regeneration for this exception. Record every failed or non-ideal result as `台球杆纯商品图观察项`, then continue to renderer.
- Do not downgrade `BLOCKED`: no usable candidate, an unreliable required measurement, or an input that cannot be prepared remains a hard stop before renderer.
- This exception does not alter Render QA. Fix renderer-only issues, such as CTA contrast or clipping, without image regeneration.

Read:

- `references/shared/copy-safety.md`
- the matching `references/resources/<resource>.md`

## Required Position Record

Title position and main-visual position are mandatory measured checks for every generated candidate. Record these values in the current-task QA notes before preparing renderer input:

```text
titleGroup: top, targetY, deltaY
mainVisual: bbox, targetCenterX, targetCenterY, deltaX, deltaY
```

- Use the resource's declared title anchor and `Title Y Range Check` for `titleGroup`.
- Define `mainVisualBBox` around only the commercially meaningful subject group required by the matching resource file. Include every visible component needed to recognize that group, such as a person and the key product they hold; exclude scenery, weak shadows, empty ground/sky, and non-critical decoration.
- Normalize the resource guide's declared main-visual rectangle to the candidate and calculate the main-visual target center with `Measured Position Correction`.
- If either required record is absent, incomplete, or cannot be measured reliably, set Pre-render QA to `BLOCKED`. Do not crop, create `material.json`, prepare renderer input, or run renderer. Obtain a clearer measurement or ask the user how to define the subject group.
- A measured positional deviation is a normal Pre-render QA failure: perform the one default targeted correction, then remeasure both required records. For a qualifying cue-only product reference, use the Cue-Only Product Exception instead: record the deviation as `台球杆纯商品图观察项` and do not regenerate. If the candidate and renderer input are usable after that retry or exception handling, record any remaining measured deviation as an observation or attention note and continue to renderer. `BLOCKED` is never downgraded to an observation.

## Spatial Layout Authority Check

Judge spatial layout against the current user request, the matching resource file, and its layout guide—not against the reference mother's original composition.

PASS only when:

- the title group's measured top or vertical center falls within the allowed range around the resource's ideal Y anchor;
- the subject's position, scale, and crop follow the guide's main-visual anchor while preserving identity and complete recognition;
- the actual title-to-subject gap, crop rules, and whitespace work for the target resource; feed/popup CTA may overlay the main visual;
- any remaining source-image similarity comes from content and visual identity, not copied coordinates.

FAIL when the candidate clearly copies the source image's title top margin, title position, subject coordinates, subject scale, crop, or whitespace and therefore misses the target resource anchors. A commercially attractive source-like composition does not override this failure.

For a targeted spatial correction, use the current candidate as the edit target and the current resource guide as the internal spatial authority. Measure the failing group's bounding box against its target anchor and record the signed deltas in the QA note. Use measured vertical/scale corrections when reliable. For main-visual horizontal centering, state the centered end result with balanced side whitespace; keep horizontal pixel/percentage deltas in QA notes only. Use the original mother only as an identity reference.

## Measured Position Correction

Calculate every position correction from the current candidate. Never reuse a fixed percentage from another candidate or substitute a visual estimate such as `上移约 7%` without recorded measurements.

For a title group, use the formula in `Title Y Range Check` below and record its `deltaY` in both pixels and canvas-height percentage in the QA note.

For the main visual group, first define `mainVisualBBox` around only the commercially meaningful subject group named by the matching resource file. Exclude sky, clouds, glow, weak shadows, empty ground, and other non-critical atmosphere. Normalize the guide's declared main-visual rectangle to the candidate, then calculate:

```text
targetMainCenterX = candidateWidth * (guideMainX + guideMainWidth / 2) / resourceWorkingCanvasWidth
targetMainCenterY = candidateHeight * (guideMainY + guideMainHeight / 2) / resourceWorkingCanvasHeight
actualMainCenterX = (mainVisualBBox.left + mainVisualBBox.right) / 2
actualMainCenterY = (mainVisualBBox.top + mainVisualBBox.bottom) / 2
mainDeltaXPx = targetMainCenterX - actualMainCenterX
mainDeltaYPx = targetMainCenterY - actualMainCenterY
mainDeltaXPct = mainDeltaXPx / candidateWidth * 100
mainDeltaYPct = mainDeltaYPx / candidateHeight * 100
```

- Negative Y means move upward; positive Y means move downward. Keep X deltas as horizontal QA diagnostics.
- Retain the unrounded pixel calculation and the canvas percentage for QA records.
- Write vertical retry prompts as short direct edits using the rounded pixel value, unless the resource declares a percentage-based title anchor. For a percentage anchor, state the target position instead, for example: `将主标题和副标题作为整体移动，使标题组顶部对齐画布顶部约 10% 的位置，其他画面元素保持不变。` Keep the rounded pixel value and percentage delta in the QA record.
- Write main-visual horizontal retry prompts with the canonical target-state template in `references/shared/background-generation.md`, replacing the generic group name with the concrete subject when useful.
- If the main visual also fails fill/scale, calculate its current width and height against the normalized guide rectangle before choosing a scale percentage. Do not use a default scale adjustment.
- If a reliable title or main-visual bounding box cannot be identified, set Pre-render QA to `BLOCKED`, record the measurement as uncertain, and stop before claiming a calculated correction. Do not crop, create `material.json`, prepare renderer input, or run renderer; obtain a clearer measurement or ask the user how to define the subject group.
- After image generation returns the corrected candidate, measure new bounding boxes from that new image. Do not treat the requested percentage as the achieved movement.

## Coordinated Title/Main-Visual Retry

Use this only when the matching resource explicitly declares it. When a title-Y correction moves the title group upward, it also moves the full main-visual subject group upward, while keeping it complete, horizontally centered, and inside the declared main-visual area.

When the main visual is visibly small, enlarge it by `5%-12%` (default about `10%`), preserve its natural aspect ratio, and do not force a tall or narrow product to fill a wide guide area. Record the title `deltaY`, main-visual `deltaY`, current and target main-visual dimensions, and selected scale change in the QA note. After generation, remeasure title and main visual independently; passing one does not override failure in the other.

## Title Y Range Check

Treat every resource-declared `titleTopAnchor` or title-group vertical-center Y as the ideal spatial target. Use the matching resource file's Pre-render QA tolerance when declared; otherwise the acceptable range is `ideal Y ± 3% of the relevant canvas height`. Use the full working-canvas height for normal resources and the lower effective material-area height for `channel` and `categoryBanner`. The title group's region height remains unconstrained.

Normalize the resource target to the actual generated candidate size before judging:

```text
if resource declares a title QA tolerance (for example feed/popup `±1%`):
    targetYOnCandidate = candidateHeight * resourceTargetRatio
    toleranceY = candidateHeight * resourceTitleQAToleranceRatio
elif normal resource:
    targetYOnCandidate = candidateHeight * resourceTargetY / resourceWorkingCanvasHeight
    relevantHeightOnCandidate = candidateHeight
    toleranceY = relevantHeightOnCandidate * 0.03
else:  # channel/categoryBanner
    targetYOnCandidate = lowerEffectiveAreaTop + lowerEffectiveAreaHeight * resourceTargetRatio
    relevantHeightOnCandidate = lowerEffectiveAreaHeight
    toleranceY = relevantHeightOnCandidate * 0.03

actualY = titleGroupBBox.top                    # titleTopAnchor resources
actualY = (titleGroupBBox.top + titleGroupBBox.bottom) / 2  # vertical-center resources
deltaY = targetYOnCandidate - actualY
deltaYPct = deltaY / candidateHeight * 100
```

- PASS the title Y check when `abs(deltaY) <= toleranceY`.
- Treat title Y as a retry-triggering miss only when `abs(deltaY) > toleranceY`.
- `deltaY < 0`: the title group is too low; move the complete title group upward by `abs(deltaY)`.
- `deltaY > 0`: the title group is too high; move the complete title group downward by `deltaY`.
- Keep the signed `deltaY` pixels and `deltaYPct` in the QA record. Use the rounded pixel distance in the retry instruction unless the resource declares a percentage-based title anchor; for that case, use the declared target-position wording. Do not use a fixed or estimated movement.
- Preserve title wording, source typography, horizontal alignment, source subtitle hierarchy, and title-group height. Do not move only one text row and do not resize the group merely to satisfy Y.
- Retry this title-Y correction once by default, using the current candidate as the only edit input. Keep the current guide as internal spatial authority; do not attach or explain it unless the correction cannot be expressed as one direct action.
- After the retry, remeasure. If the title Y is still outside the allowed range but the renderer input can be prepared, record the remaining direction and distance as a warning and continue to renderer. Do not run a second title-Y retry by default.
- This continuation applies to every remaining Pre-render QA deviation. Record the concrete impact as an observation or attention note, then continue to renderer without waiting for confirmation.

## Semantic Layout Judgment

Use this before deciding whether a layout deviation needs targeted regeneration.

For non-channel resources, treat the guide's title and main-visual anchors as the primary spatial judge while keeping the blue title region free of a fixed-height requirement. Use the blue mark for horizontal alignment plus the resource's ideal top/center Y anchor and its Pre-render QA tolerance; do not fail or resize a title group merely because it crosses the blue region's bottom. First identify the real main visual: product bodies, people/faces, screens, packaging, and props that carry commercial recognition. Do not count sky, clean background, weak shadows, empty desk, clouds, glow, or other non-critical atmosphere as real main visual.

A title/subtitle group or subject that crosses the numeric guide boundary is not an automatic FAIL when all of these are true:

- The title group's top Y or vertical-center Y remains within the allowed range; only the blue region's fixed height/bottom boundary is exceeded.
- The reference image intentionally uses a large campaign title, or the user asks to preserve the original text form.
- The migrated title/subtitle do not cover, cut, deform, or visually compete with the real main visual.
- The real main visual remains complete, readable, and commercially strong.
- The bottom composition remains usable; feed/popup CTA may overlay the main visual.
- The larger or boundary-crossing title/subtitle group does not force the main visual group away from its declared main-visual area center.
- The generated background is free of a baked CTA and visible guide/template structure, and it contains one readable, unclipped, single-row main title group.

In that case, mark Pre-render QA as `PASS with observation` and continue to renderer. Record the concrete observation, for example: `标题组纵向延展较大，但只影响非关键背景；主视觉位置、主体识别和 CTA 区仍可用。`

A title Y outside the allowed range always triggers its one directional retry even when the composition otherwise looks acceptable, except for a qualifying cue-only product reference under the Cue-Only Product Exception. For other layout deviations, trigger targeted regeneration only when the generated background itself creates a real visual problem: it covers a face/product/screen, weakens or shrinks the subject, makes the title/main visual relationship confusing, clips or splits copy, duplicates title positions, or exposes template structure. Future CTA overlap is an observation rather than a regeneration trigger.

## Oversized Title Group Correction

Use title/subtitle scale-down only when the title/subtitle group itself causes a real collision, clipping, harmful visual dominance, or layout compression. Judge its size by those real visual effects rather than the guide's blue title shape or a future CTA overlap.

Before choosing title scale-down, check both conditions:

- The title/subtitle group creates a real collision, clipping, readability problem, or harmful visual dominance; crossing the guide's former title-region height alone does not satisfy this condition.
- That oversized title/subtitle group causes layout compression, weakens the intended title-main-visual gap, or pushes the main visual group away from its declared area center.

If the title/subtitle group remains visually sound, keep its size and correct only the main visual placement or scale that actually needs adjustment.

When both oversized-title conditions are true, mark Pre-render QA as FAIL and retry with a targeted correction:

- preserve title wording, alignment, and source typography style and hierarchy;
- reduce the title/subtitle group mildly by `5%-8%` by default, around `6%` unless the oversize is extreme;
- move the title/subtitle group only as much as needed to relieve layout compression; do not force it inside the guide's former title-region height;
- rebalance the main visual group toward the declared main-visual area center;
- do not solve the issue by shrinking the main visual into weakness.

## Targeted Retry Routing

Choose the retry input by failure type:

- **Position or scale:** edit the current candidate and use the current guide as internal spatial authority. Use a concise measured action for vertical/scale correction. For main-visual horizontal centering, describe the centered end state with balanced side whitespace and keep X deltas in QA notes only. Move the complete title or subject group and keep other elements unchanged.
- **Copy:** edit the current candidate with the current guide. Restore exact missing, wrong, duplicated, clipped, or effectively unreadable title/subtitle copy; preserve the source font style and subtitle hierarchy; use the required alignment and one-row horizontal main title; remove only duplicated copy left in the old position. Preserve the subject and composition. Use this route when the subtitle visibly drifts from the source typography.
- **Subject fidelity:** restart from the original mother image plus the current guide. Restore the same people/products, count, appearance, and scene logic; do not use a drifted candidate as the primary visual source.
- **Visible template or baked CTA:** when the issue is local, edit the current candidate and remove only the visible guide/template/CTA. When it affects the full composition, restart from the original mother image plus the current guide.

Run the full Pre-render QA after the retry. Record every remaining deviation as an observation or attention note, then continue to renderer without waiting for confirmation.

## Buffered Horizontal Boundary Correction

Use this for `channel` and `categoryBanner` boundary failures:

```text
boundaryY = generatedImageHeight * 0.49
effectiveHeight = generatedImageHeight - boundaryY
subjectTopY / subjectBottomY = meaningful subject bounding box
overflowPx = max(0, boundaryY - subjectTopY)
bottomSlackPx = max(0, generatedImageHeight - subjectBottomY)
safetyPx = max(12, effectiveHeight * 0.04)
requiredDownshiftPx = overflowPx + safetyPx
downshiftPct = ceil(requiredDownshiftPx / effectiveHeight * 100)
scaleDownPct = 0 if requiredDownshiftPx <= bottomSlackPx, otherwise ceil((requiredDownshiftPx - bottomSlackPx) / (subjectBottomY - subjectTopY) * 100) + 10
```

Clamp `downshiftPct` to `8%-35%` and nonzero `scaleDownPct` to `12%-45%`. Keep subject size when `scaleDownPct=0`; otherwise shrink and move the full subject group together. Keep its highest meaningful point below `y=49%`.

PASS only when:

- Subject fidelity is preserved: no unrelated products, people, props, visual categories, or cross-task elements.
- The candidate follows the matching resource layout guide and resource-specific rules, or has an acceptable semantic layout deviation under the judgment above.
- For non-channel resources, the candidate looks like one continuous generated background extended from the reference image, with the layout guide used only as invisible placement reference.
- For `channel`, the candidate follows the lower-effective-area rule: upper white crop buffer remains empty, the boundary is a straight horizontal hard edge, and all rendered content stays in the lower material area.
- When the resource file declares approximate percentage ranges for subject, CTA, crop buffers, or safe areas, the candidate is checked against those ranges and then judged semantically for real visual harm before retrying. Do not check title-group height against a fixed blue-region range.
- Core product/person/main visual content lands in the guide's red area; migrated title/subtitle align with the guide's blue anchor horizontally and remain readable, unclipped, and separated from the main visual. Their vertical extent may exceed the blue guide shape.
- Source or user-provided title/subtitle are visible within the generated image's allowed title-group Y range and at its horizontal alignment anchor.
- The title top margin or vertical center and the main visual's position/scale follow the target resource layout rather than the source image's original spatial relationships.
- Migrated title/subtitle preserve the source wording, color family, general campaign character, and font style, unless the user explicitly requested a title-design change.
- The migrated main title is exactly one visual text row unless the user explicitly approved another treatment. All source main-title segments are joined into that row; no main-title phrase is stacked above or below another phrase.
- Horizontal resources use left-aligned title/subtitle; square and vertical resources use horizontally centered title/subtitle.
- The generated background contains no CTA button.
- The title/subtitle group is readable for the requested text color or a faithful color adapted from the reference.
- The subtitle is present, correct, unclipped, generally readable, and visually faithful to the source typography. Minor raster variation alone is an observation.
- Main subjects are not cut, deformed, replaced, or made commercially weak.
- Bottom/crop-buffer rules from the resource file are satisfied.
- Feed/popup CTA may overlay the main visual; record the overlap after rendering and continue when the CTA is visible, unclipped, and distinguishable from its local background.

FAIL means:

- For a qualifying cue-only product reference under the Cue-Only Product Exception, do not regenerate. Record the concrete issue as `台球杆纯商品图观察项` and continue to renderer when the candidate is usable and not `BLOCKED`.
- For every non-qualifying reference, do not crop, create `material.json`, or run renderer until the one default targeted retry and the second Pre-render QA are complete.
- For every non-qualifying reference, write the concrete visual/copy failure, including whether the problem actually affects the real main visual or CTA area; regenerate once with a targeted correction by default; run the full Pre-render QA again; then record every remaining deviation as an observation or attention note and continue to renderer without waiting for confirmation.

Only stop before renderer when there is no usable generated candidate, the renderer input cannot be prepared, or Pre-render QA is `BLOCKED` because a required title/main-visual position record is missing or unreliable. Those cases must be reported as hard blockers.

Treat split main titles as a concrete copy failure: if the main title appears as two or more visual rows, or if the candidate preserves the reference image's multi-line main-title layout without explicit user approval, Pre-render QA fails even when the title is readable and aligned to the correct title anchor.

Do not change only the subtitle's size, weight, or tracking to satisfy an abstract rule. A missing, wrong, duplicated, clipped, effectively unreadable, or visibly style-drifted subtitle remains an objective copy failure and may be restored through the general copy route.

Treat visible template structure as a concrete visual failure: if the result looks like a visible template instead of one continuous generated background, including visible guide colors, panels, frames, cards, title bars, image containers, or pasted-photo composition, Pre-render QA fails.

If image generation returns no usable candidate, Pre-render QA is not reached. Stop and ask whether to retry generation.

## Render QA

Run after renderer completes.

Check:

- output file exists and is nonzero
- expected dimensions
- rounded transparent corners when renderer expects them
- title/subtitle generated by image gen remain visible and not clipped
- for `feed` and `popup`, renderer CTA is visible and not clipped
- for `feed` and `popup`, CTA background is distinguishable from its local background
- for `feed` and `popup`, record CTA overlap as an observation without changing PASS/FAIL status

Renderer technical PASS does not override visible copy clipping or obvious visual failure.

On Render QA failure:

- **File, dimensions, or transparent corners:** fix the renderer/input and render again; do not regenerate the image.
- **Title/subtitle clipped:** for `channel` or `categoryBanner`, rerun preparation with the complete `--title-bbox`; for other resources, first fix renderer scaling/cropping. Regenerate only when the prepared source is already clipped.
- **Feed/popup CTA blends into the local background:** change only the button colors in `material.json`, then render again.
- **Feed/popup CTA is clipped:** fix the renderer button configuration, then render again.

Run Render QA again after the correction. Do not deliver while any Render QA item fails.

Do not require, read, summarize, or deliver `qa-report.md` / `qa-report.json` in default fast mode.
