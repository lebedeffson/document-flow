#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[verify] stack"
bash ops/check_stack.sh

echo
echo "[verify] naudoc profiles"
bash rukovoditel-test/sync_naudoc_profiles.sh

echo
echo "[verify] smoke"
bash ops/smoke_test_stack.sh

echo
echo "[verify] full contour"
python3 ops/full_contour_audit.py

echo
echo "[verify] ecosystem"
python3 ops/audit_ecosystem_integration.py

echo
echo "[verify] onlyoffice backend"
python3 ops/audit_onlyoffice_integration.py

echo
echo "[verify] onlyoffice browser"
PLAYWRIGHT_BROWSER=chromium node ops/onlyoffice_browser_e2e.mjs

echo
echo "[verify] onlyoffice firefox"
PLAYWRIGHT_BROWSER=firefox node ops/onlyoffice_browser_e2e.mjs

echo
echo "[verify] sidebar ui"
timeout 240 node ops/sidebar_ui_audit.mjs

echo
echo "[verify] collect logs"
bash ops/collect_runtime_logs.sh

echo
echo "[verify] all checks passed"
