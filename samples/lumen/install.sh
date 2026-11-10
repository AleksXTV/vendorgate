#!/usr/bin/env bash
# Installs Lumen Sans fonts for the current user only (macOS or Linux).
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)/fonts"
if [[ "$(uname)" == "Darwin" ]]; then
  DEST="$HOME/Library/Fonts"
else
  DEST="$HOME/.local/share/fonts/lumen"
fi
mkdir -p "$DEST"
cp "$SRC"/LumenSans-*.otf "$DEST"/
command -v fc-cache >/dev/null && fc-cache -f "$DEST" || true
echo "Lumen Sans installed to $DEST"
