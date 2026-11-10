#!/usr/bin/env bash
# One command after you have a Clocked API key:
#   export CLOCKED_API_KEY=...   (or put it in .env)
#   bash scripts/finish.sh
# It records live runs of the three sample packets into recorded/, renders
# their Markdown memos, records the demo video and screenshots, and commits.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . ./.env && set +a
: "${CLOCKED_API_KEY:?Set CLOCKED_API_KEY first}"
python3 -m venv .venv 2>/dev/null || true
. .venv/bin/activate
pip install -q -r requirements.txt playwright pytest
python -m playwright install chromium >/dev/null
python -m pytest -q tests
for s in northwind quickpixel lumen; do
  python -m vendorgate review "samples/$s" --save "recorded/$s.json" --markdown "recorded/$s.md"
done
python scripts/record_demo.py
git add recorded docs demo/vendorgate-demo.mp4 2>/dev/null || true
git commit -qm "Recorded live runs, screenshots and demo video" || true
echo "Done: demo/vendorgate-demo.mp4, docs/screenshot-*.png, recorded/*.json"
