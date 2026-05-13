#!/bin/bash
# Wrapper script for Chrome Native Messaging Host
# Chrome calls this, which in turn launches the Python bridge
exec /opt/anaconda3/bin/python3 /Users/wuwanglong/work2/obsidian/AGIKnowledge/.claude/skills/summary-inbox/scripts/bookmark_bridge.py
