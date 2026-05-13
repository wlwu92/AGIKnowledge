---
name: tag-normalizer
description: Normalize Obsidian AGIKnowledge tags across notes; audit duplicate, mixed-language, case, emoji, inline-array, and per-note ad hoc tags; maintain the central canonical tag registry before writing or rewriting notes.
---

# Tag Normalizer

Use this skill whenever creating, reviewing, or normalizing tags in this vault.

**Announce at start:** "Using tag-normalizer skill to keep vault tags consistent."

## Source of Truth

Read `99_索引与地图 (Index & Maps)/标签体系.md` first. It is the canonical tag registry and alias map.

## Core Rules

- Tags are global retrieval axes, not per-note keywords.
- Use lowercase English kebab-case with hierarchy: `domain/cv`, `topic/3d-reconstruction`, `method/slam`.
- Do not create Chinese tags, emoji tags, uppercase variants, inline one-off keywords, or near duplicates.
- Every formal note must include exactly one `layer/*` tag and at least one `type/*` tag. Put the primary type first; `type/moc` may be a secondary type for survey/index notes.
- Prefer 5-8 tags per note. Add more only when each tag enables a distinct future query.
- Preserve proper nouns in `aliases`, headings, and body text; normalize them in tags only when they are stable retrieval axes.

## Workflow

1. Inspect existing context:
   - Read the central tag registry.
   - Search existing notes for related tags and titles before choosing new tags.
   - Check whether the note belongs to an existing MOC/survey cluster.
2. Normalize frontmatter:
   - Prefer block YAML lists over inline arrays.
   - Keep `source`, `created`, `aliases`, `status`, and other metadata.
   - Put tags in this order: `layer/*`, `type/*`, `domain/*`, `topic/*`, `method/*`, `entity/*`, `venue/*`.
3. Reuse before creating:
   - If an old or candidate tag maps to a registry tag, use the registry tag.
   - If the concept is too narrow for the registry, mention it in the body instead of adding a tag.
   - Add a new registry tag only if it is expected to recur or represents an important knowledge axis.
4. After changes:
   - Re-scan tags for uppercase, Chinese, emoji, spaces, underscores, and inline-array drift.
   - If new tags were added, update the registry and alias table.

## Frontmatter Pattern

```yaml
---
source: "https://example.com"
created: 2026-05-12
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

## Classification Hints

- Research project or paper: `type/paper`.
- Installable repository or engineering utility: `type/tool`.
- Broad synthesis across multiple notes: `type/survey`; add `type/moc` only if the note is also an index/navigation hub.
- Original clipped source: `type/clipping`.
- Market or securities material: `type/report`.
- Use `entity/*` sparingly for durable models, systems, labs, or frameworks that users will search as entities.

## Useful Audits

```bash
python3 .claude/skills/tag-normalizer/scripts/audit_tags.py .
rg -n "^tags: \\[" .
```
