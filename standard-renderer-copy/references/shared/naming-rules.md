# Naming Rules

## Resource Aliases

```text
中通 / 频道页中通                  -> channel
分类 / 分类筛选 / 分类筛选Banner    -> categoryBanner
Push / push / 消息页Push            -> push
feed / Feed                         -> feed
弹窗                                -> popup
开屏                                -> splash
```

## Resource Files

```text
channel        -> references/resources/channel.md
categoryBanner -> references/resources/category-banner.md
push           -> references/resources/push.md
feed           -> references/resources/feed.md
popup          -> references/resources/popup.md
splash         -> references/resources/splash.md
```

## Preferred Input Filenames

```text
channel.png
categoryBanner.png
push.png
feed.png
popup.png
splash.png
```

Business prefixes are allowed when explicit `material.json.images` mapping is used.

## Task Folder Rules

Every request with a provided reference image must create a new task-specific input folder and output group.

Task identity is based on:

```text
current reference image + current request block + timestamp/sequence
```

Task identity is not based on:

```text
title / subtitle / cta / colors / resource positions
```

Recommended folder names:

```text
task_YYYYMMDD_HHMMSS_<short_theme>_<resources>
task_YYYYMMDD_001_<short_theme>_<resources>
```

Keep prior task folders and output groups unchanged unless the user explicitly asks to modify or delete them.

## Shared Background

When one task requests both `channel` and `categoryBanner`, they must share one AI-generated horizontal work image. Generate it once with the `channel` rules, retain it as `shared-horizontal.png` (or an explicitly mapped equivalent), then derive `channel.png` and `categoryBanner.png` with their respective preprocessors. Do not generate a second category Banner background.

Mention in delivery notes:

```text
categoryBanner 由 channel 横图共享生成。
```
