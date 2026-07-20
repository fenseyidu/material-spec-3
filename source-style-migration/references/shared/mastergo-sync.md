# MasterGo Sync

Use this only when the user explicitly asks to update local specs from a MasterGo URL or layer ID.

## Rules

- Read MasterGo data; do not edit MasterGo online files.
- Do not update Feishu docs unless the user confirms the exact document and target change.
- Preserve local raw DSL caches when useful.
- Update only the matching resource in `assets/material-renderer/templates.mjs`.
- Keep the "no separate visual-subject slot" rule.

## Known Layer Map

```text
12:91     channel
12:340    categoryBanner
12:0187   push
12:034    feed
12:294    popup
12:0022   splash
```

Older raw caches may contain `12:369` for an old push size. The current push layer is `12:0187`.

## After Sync

Run the affected template and report the changed fields and output path.
