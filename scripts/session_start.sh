#!/usr/bin/env bash
# SessionStart hook: install deps and fetch data so every cloud session starts ready. Quiet and idempotent.
cd "$(dirname "$0")/.." || exit 0
python3 -m pip install -q -r requirements.txt >/dev/null 2>&1 || echo "session_start: pip install failed"
bash scripts/fetch_data.sh >/dev/null 2>&1 || echo "session_start: fetch_data failed (run bash scripts/fetch_data.sh)"
exit 0
