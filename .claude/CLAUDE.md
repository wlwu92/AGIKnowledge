# Obsidian AGIKnowledge Vault

## 项目结构

- `.claude/skills/summary-inbox/` — 处理 Chrome 书签的 Skill
- `.claude/skills/tag-normalizer/` — 统一标签体系与审计的 Skill

## Skills

- `summary-inbox` — 从 Chrome Inbox 读取书签，获取内容后分类写入 vault，再归档。调用方式：`/summary-inbox`
- `tag-normalizer` — 维护 `AGIKnowledge` 的统一标签体系，规范重复、混合语言、大小写和临时标签。整理新笔记或批量改标签前先用它。

## 知识库整理契约

- 正式笔记必须先查 `99_索引与地图 (Index & Maps)/标签体系.md`，再写 frontmatter 标签。
- 每篇正式笔记必须包含 1 个 `layer/*` 和至少 1 个 `type/*` 标签；主类型放在最前。
- 标签统一使用小写英文层级格式，例如 `domain/cv`、`topic/3d-reconstruction`、`venue/cvpr-2025`。
- 新笔记应先搜索相邻笔记和 MOC/survey，避免只按单条资料孤立整理。

## 基础设施

### Chrome Extension: Summary Inbox Bridge

路径: `.claude/skills/summary-inbox/chrome-bridge/`

这个扩展通过 Native Messaging 桥接 `chrome.bookmarks.*` API，实现不重启 Chrome 的书签移动操作。

**安装步骤：**
1. 打开 `chrome://extensions` → 开启开发者模式 → 加载解压的扩展 → 选择 `chrome-bridge/`
2. 复制扩展 ID → `bash .claude/skills/summary-inbox/scripts/install.sh --configure <ext-id>`
3. 重启 Chrome 使 Native Messaging Host 生效

**验证：** `python3 .claude/skills/summary-inbox/scripts/bookmark_bridge.py findFolder Inbox`
