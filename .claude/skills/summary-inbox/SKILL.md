---
name: summary-inbox
description: Consume Chrome bookmarks from the Inbox folder; fetch content, classify into the Obsidian vault, write structured tag-normalized notes, update related MOC/survey context, and archive processed items.
---

# Summary Inbox

Consume Chrome bookmarks from a cloud-synced **Inbox** folder. For each bookmark: fetch content, classify into the Obsidian vault's L1–L4 hierarchy, write a structured and tag-normalized note, then move the bookmark to an **Archives** folder (dedup by URL).

**Announce at start:** "Using summary-inbox skill to process Chrome bookmarks."

## Prerequisites

- Chrome bookmarks bar has an **Inbox** folder and an **Archives** folder
- Obsidian vault at `~/work2/obsidian/AGIKnowledge/`
- Vault structure per `.claude/CLAUDE.md` (L1–L4 hierarchy)
- **Summary Inbox Bridge** Chrome extension loaded (see `chrome-bridge/`)
- Native messaging host registered (run `scripts/install.sh` then `scripts/install.sh --configure <ext-id>`)
- Tag registry at `99_索引与地图 (Index & Maps)/标签体系.md`

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│  This Skill (Claude Code)                        │
│    → Reads Bookmarks JSON directly (for listing) │
│    → Calls bookmark_bridge.py CLI for writes     │
└─────────────┬───────────────────────────────────┘
              │ Unix Socket
              ▼
┌─────────────────────────────────────────────────┐
│  bookmark_bridge.py (Native Messaging Host)      │
│    → stdin/stdout ↔ Chrome Extension             │
│    → Unix socket ↔ CLI commands                  │
└─────────────┬───────────────────────────────────┘
              │ Native Messaging (JSON over stdin/stdout)
              ▼
┌─────────────────────────────────────────────────┐
│  Summary Inbox Bridge Extension (Service Worker) │
│    → chrome.bookmarks.* API                      │
└─────────────┬───────────────────────────────────┘
              │
              ▼
         Chrome Bookmarks
```

**Key insight:** Reads are done by parsing the Bookmarks JSON file directly (reliable while Chrome runs). Writes (moving to Archives) go through the extension bridge, using `chrome.bookmarks.*` API — no Chrome restart needed, no checksum issues, full Sync compatibility.

## The Process

### Step 1: Ensure Chrome Is Running

Chrome must be running for the extension + native messaging bridge to work.

```
pgrep -x "Google Chrome" > /dev/null || open -a "Google Chrome"
sleep 3
```

### Step 2: Read Inbox Bookmarks

Parse Bookmarks JSON with Python — always reliable, no AppleScript needed:

```python
import json, os

path = os.path.expanduser(
    "~/Library/Application Support/Google/Chrome/Default/Bookmarks"
)
with open(path, "r") as f:
    data = json.load(f)

def walk_children(nodes, target_name, parent_name=""):
    """Recursively find bookmarks in a named folder."""
    results = []
    for node in nodes:
        if node.get("type") == "folder" and node.get("name") == target_name:
            for child in node.get("children", []):
                if child.get("type") == "url":
                    results.append((child["name"], child["url"]))
        if "children" in node:
            results.extend(walk_children(node["children"], target_name, node.get("name")))
    return results

inbox = walk_children(
    [data["roots"]["bookmark_bar"]], "Inbox"
)
```

### Step 3: Dedup Against Archives

Read the Archives folder from the same JSON file. Scan for URLs matching Inbox items.

### Step 4: Fetch and Classify

For each new bookmark:
1. Fetch page content with WebFetch (or WebSearch as fallback)
2. Read `99_索引与地图 (Index & Maps)/标签体系.md` and search related existing notes. Do not tag in isolation.
3. Classify to L1–L4:
   - **L1**: Math, info theory, cognitive science, stats, optimization
   - **L2**: Model architecture, training, CV/NLP/Robotics algorithms
   - **L3**: Training frameworks, inference optimization, MLOps, AI Infra
   - **L4**: LLM apps, embodied AI, agents, safety, tools/workflows
4. Decide note type:
   - `type/paper`: paper, research project, algorithm work
   - `type/tool`: installable repo, framework, utility
   - `type/survey`: broad synthesis across multiple notes
   - `type/moc`: navigation/index hub
   - `type/report`: industry or market report
5. Check for existing note by searching `source: "<url>"` in vault. If found, skip or update.
6. Write note: `YYYY-MM-DD-ShortSlug-中文描述.md` with normalized frontmatter:
   ```yaml
   ---
   source: "<url>"
   created: <YYYY-MM-DD>
   aliases:
     - ShortName
   tags:
     - layer/l2
     - type/paper
     - domain/cv
     - topic/3d-reconstruction
     - method/transformer
     - venue/cvpr-2025
   ---
   ```
   Tag order is always: `layer/*`, `type/*`, `domain/*`, `topic/*`, `method/*`, `entity/*`, `venue/*`.

### Note Structure Contract

Choose the narrowest useful template and keep the section names stable.

**Research / paper note**

```markdown
# WorkName — 中文说明

## 概述

## 核心贡献

## 方法机制

## 关联笔记

## 判断与局限
```

**Tool / repo note**

```markdown
# ToolName — 中文说明

## 用途

## 核心能力

## 使用方式

## 适用边界

## 关联笔记
```

**Survey / MOC note**

```markdown
# 主题综述

## 覆盖范围

## 发展脉络

## 核心对比

## 知识地图

## 关联笔记
```

### Consistency Rules

- Prefer one strong note over many shallow duplicates. If the bookmark extends an existing cluster, update the existing survey/MOC links.
- Use canonical tags from `标签体系.md`; never invent `CV`/`3D重建`/`Compute Vision` style variants.
- Keep source facts separate from interpretation: facts in `概述`/`方法机制`, judgment in `判断与局限`.
- Use wiki links for durable relationships. Prefer `[[filename|display name]]` and keep display names short.
- Do not use tags for temporary status such as "已整理"; use `status: processed` in raw clipping frontmatter.

### Step 5: Archive via Chrome Extension Bridge

Move processed bookmarks from Inbox to Archives using the Chrome Extension bridge:

```bash
python3 scripts/bookmark_bridge.py moveBookmark --url "https://..." --target "Archives"
```

For batch moves (multiple bookmarks at once, faster):

```bash
python3 scripts/bookmark_bridge.py --json '{
  "cmd": "moveBookmark",
  "url": "https://example.com",
  "targetFolder": "Archives"
}'
```

This sends the command over a Unix socket to the native messaging host, which forwards it to the Chrome extension. The extension executes `chrome.bookmarks.move()` and the bookmark is updated in real-time — no Chrome restart, no AppleScript, no JSON file tampering.

If the Archives folder doesn't exist, the extension creates it automatically under Other Bookmarks.

### Step 6: Output Summary

| Bookmark | Result | Note |
|----------|--------|------|
| Title | ✅ New / ⏭️ Dup / 📝 Updated / ❌ Failed | `Lx/file.md` |

## Error Handling

- WebFetch fails → WebSearch fallback → skip if both fail
- Note write fails → keep in Inbox, report
- First item failure doesn't stop others
- Bridge unavailable → print instructions to check Chrome/extension
- Bridge timeout (30s) → bookmark stays in Inbox, report for manual retry
