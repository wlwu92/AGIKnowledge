#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BRIDGE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CHROME_BRIDGE_DIR="$BRIDGE_DIR/chrome-bridge"
TEMPLATE="$SCRIPT_DIR/com.claude.summary_inbox.json"
WRAPPER="$SCRIPT_DIR/native_host.sh"

NATIVE_HOST_DIR="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts"
NATIVE_HOST_FILE="$NATIVE_HOST_DIR/com.claude.summary_inbox.json"

echo "=== Summary Inbox Bridge Installer ==="
echo ""

# Step 1: Install native messaging host manifest
echo "[1/3] Installing native messaging host manifest..."
mkdir -p "$NATIVE_HOST_DIR"

# Make wrapper executable
chmod +x "$WRAPPER"

cp "$TEMPLATE" "$NATIVE_HOST_FILE"

# Replace placeholders
if [[ "$(uname)" == "Darwin" ]]; then
  sed -i '' "s|__WRAPPER_SCRIPT_PATH__|$WRAPPER|" "$NATIVE_HOST_FILE"
else
  sed -i "s|__WRAPPER_SCRIPT_PATH__|$WRAPPER|" "$NATIVE_HOST_FILE"
fi

echo "  -> $NATIVE_HOST_FILE"
echo ""

# Step 2: Load Chrome extension
echo "[2/3] Chrome extension ready at:"
echo "  -> $CHROME_BRIDGE_DIR"
echo ""
echo "  Open chrome://extensions in Chrome"
echo "  Enable 'Developer mode' (top right)"
echo "  Click 'Load unpacked'"
echo "  Select: $CHROME_BRIDGE_DIR"
echo ""

# Step 3: Configure extension ID
if [[ "${1:-}" == "--configure" && -n "${2:-}" ]]; then
    EXT_ID="$2"
    echo "[3/3] Configuring native host for extension ID: $EXT_ID"
    if [[ "$(uname)" == "Darwin" ]]; then
      sed -i '' "s|__EXTENSION_ID__|$EXT_ID|" "$NATIVE_HOST_FILE"
    else
      sed -i "s|__EXTENSION_ID__|$EXT_ID|" "$NATIVE_HOST_FILE"
    fi

    echo ""
    echo "✅ Done! Please reload the extension at chrome://extensions, then verify:"
    echo "    python3 \"$SCRIPT_DIR/bookmark_bridge.py\" findFolder Inbox"
    echo ""
fi

# Check if still need configuration
if grep -q '__EXTENSION_ID__' "$NATIVE_HOST_FILE" 2>/dev/null; then
    echo "⚠️  Native host manifest still needs the extension ID."
    echo ""
    echo "  After loading the extension at chrome://extensions:"
    echo "  Copy its ID and run:"
    echo "    $0 --configure <extension-id>"
    echo ""
fi
