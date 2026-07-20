# Material Spec Skill

根据参考图中的主、副标题，将运营物料任务路由到合适的本地工作流。

## 工作流

- `source-style-migration/`：保留原图主、副标题的字体与视觉样式，并迁移至标准资源位。
- `standard-renderer-copy/`：清除图内主、副标题，使用标准模板绘制标题、副标题与 CTA。
- 根目录 `SKILL.md` 只负责检查图片并路由：含图内主、副标题时由用户选择工作流；不含图内主、副标题且已提供文字时，直接使用标准文字模板。

## 共享能力

- 支持频道页中通、分类筛选 Banner、消息页 Push、feed、弹窗、开屏；原图迁移工作流额外支持小程序分享图。
- 两条工作流共用根目录 `assets/fonts/` 中的字体，使用 Python/Pillow 本地渲染并校验成图规格。
- 输入和输出任务文件始终写在 skill 外的工作区，避免污染 skill 本体。

## 版本记录

每次发布前更新 [CHANGELOG.md](CHANGELOG.md)，说明新增、修改和修复的功能。
