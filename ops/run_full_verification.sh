#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# shellcheck source=lib/runtime_env.sh
source "${ROOT_DIR}/ops/lib/runtime_env.sh"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

if [ ! -d ops/node_modules/playwright ]; then
  echo "[verify] bootstrap playwright"
  npm install --prefix ops --no-fund --no-audit
fi

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
echo "[verify] onlyoffice firefox"
PLAYWRIGHT_BROWSER=firefox node ops/onlyoffice_browser_e2e.mjs

echo
echo "[verify] sidebar ui"
PLAYWRIGHT_BROWSER=firefox timeout 240 node ops/sidebar_ui_audit.mjs

echo
echo "[verify] onlyoffice chromium"
PLAYWRIGHT_BROWSER=chromium node ops/onlyoffice_browser_e2e.mjs

echo
echo "[verify] deep module audit"
PLAYWRIGHT_BROWSER=chromium node ops/deep_module_browser_audit.mjs

echo
echo "[verify] collect logs"
bash ops/collect_runtime_logs.sh

echo
echo "[verify] all checks passed"
