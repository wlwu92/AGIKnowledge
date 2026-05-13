#!/usr/bin/env python3
"""Audit AGIKnowledge frontmatter tags against the canonical registry."""

from __future__ import annotations

import re
import sys
from pathlib import Path


TAG_RE = re.compile(r"^[a-z0-9]+/[a-z0-9][a-z0-9-]*(?:/[a-z0-9][a-z0-9-]*)*$")
REGISTERED_RE = re.compile(r"`([^`]+/[a-z0-9][a-z0-9\-/]*)`")


def frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1]


def extract_tags(fm: str, path: Path, issues: list[str]) -> list[str]:
    tags: list[str] = []
    in_tags = False
    for line in fm.splitlines():
        if line.startswith("tags:"):
            if "[" in line:
                issues.append(f"{path}: inline tags are not allowed: {line.strip()}")
            in_tags = True
            continue
        if in_tags:
            if line.startswith("  - "):
                tags.append(line[4:].strip().strip("\"'"))
            elif line and not line.startswith(" "):
                in_tags = False
    return tags


def is_formal_note(path: Path) -> bool:
    return any(part.startswith(("01_", "02_", "03_", "04_")) for part in path.parts)


def main() -> int:
    vault = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    registry_path = vault / "99_索引与地图 (Index & Maps)" / "标签体系.md"
    if not registry_path.exists():
        print(f"missing registry: {registry_path}", file=sys.stderr)
        return 2

    registry = registry_path.read_text(encoding="utf-8")
    registered = set(REGISTERED_RE.findall(registry))
    issues: list[str] = []
    used: set[str] = set()
    files = 0

    for path in sorted(vault.rglob("*.md")):
        fm = frontmatter(path.read_text(encoding="utf-8"))
        if fm is None:
            continue
        files += 1
        tags = extract_tags(fm, path, issues)
        used.update(tags)

        for tag in tags:
            if not TAG_RE.match(tag):
                issues.append(f"{path}: non-canonical tag: {tag}")
            if tag not in registered:
                issues.append(f"{path}: tag not registered: {tag}")

        if is_formal_note(path):
            layer_tags = [tag for tag in tags if tag.startswith("layer/")]
            type_tags = [tag for tag in tags if tag.startswith("type/")]
            if len(layer_tags) != 1:
                issues.append(f"{path}: expected exactly one layer/* tag, got {layer_tags}")
            if not type_tags:
                issues.append(f"{path}: expected at least one type/* tag")

    print(f"audited_files: {files}")
    print(f"unique_tags: {len(used)}")
    print(f"issues: {len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
