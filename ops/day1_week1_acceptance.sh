#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

OUT_DIR="${ROOT_DIR}/runtime/monitoring/day1-week1-acceptance"
PLAYWRIGHT_BROWSER="${PLAYWRIGHT_BROWSER:-firefox}"
RUN_DEEP_AUDIT=1

usage() {
  cat <<'EOF'
Usage:
  bash ops/day1_week1_acceptance.sh [options]

Options:
  --skip-deep-audit     Skip the long deep browser audit
  --browser <name>      Browser for ONLYOFFICE/role acceptance (default: firefox)
  -h, --help            Show help
EOF
}

fail() {
  echo "[day1-week1] ERROR: $*" >&2
  exit 1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skip-deep-audit)
      RUN_DEEP_AUDIT=0
      shift
      ;;
    --browser)
      PLAYWRIGHT_BROWSER="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown option: $1"
      ;;
  esac
done

mkdir -p "${OUT_DIR}"

have_playwright_runtime() {
  if ! command -v node >/dev/null 2>&1; then
    return 1
  fi

  local probe_js
  probe_js="$(mktemp)"
  cat > "${probe_js}" <<'EOF'
import('playwright')
  .then(() => process.exit(0))
  .catch(() => process.exit(1));
EOF

  if node "${probe_js}" >/dev/null 2>&1; then
    rm -f "${probe_js}"
    return 0
  fi

  rm -f "${probe_js}"
  return 1
}

run_step() {
  local name="${1:-}"
  shift
  local log_path="${OUT_DIR}/${name}.log"

  echo "[day1-week1] ${name}"
  if "$@" >"${log_path}" 2>&1; then
    echo "[day1-week1] ${name}: ok"
    return 0
  fi

  echo "[day1-week1] ${name}: failed" >&2
  cat "${log_path}" >&2
  return 1
}

run_step "check_stack" bash "${ROOT_DIR}/ops/check_stack.sh"
run_step "prod_readiness" python3 "${ROOT_DIR}/ops/prod_readiness_audit.py"
run_step "monitoring_snapshot" python3 "${ROOT_DIR}/ops/monitoring_snapshot.py"
run_step "ecosystem_audit" python3 "${ROOT_DIR}/ops/audit_ecosystem_integration.py"
run_step "live_office_frontdoors" python3 "${ROOT_DIR}/ops/audit_live_office_frontdoors.py"
if [ -n "${DOCSPACE_TARGET_URL:-}" ] || [ -n "${WORKSPACE_TARGET_URL:-}" ]; then
  run_step "live_office_auth" node "${ROOT_DIR}/ops/audit_live_office_auth.mjs"
fi
run_step "onlyoffice_backend" python3 "${ROOT_DIR}/ops/audit_onlyoffice_integration.py"
if have_playwright_runtime; then
  run_step "word_doctor_browser" env \
    PLAYWRIGHT_BROWSER="${PLAYWRIGHT_BROWSER}" \
    DOCFLOW_LOGIN_USER=doctor \
    DOCFLOW_LOGIN_PASSWORD=test2026 \
    ONLYOFFICE_ITEM_PATH=25-14 \
    ONLYOFFICE_EXPECT_DOCUMENT_TYPE=word \
    node "${ROOT_DIR}/ops/onlyoffice_browser_e2e.mjs"
  run_step "excel_head_browser" env \
    PLAYWRIGHT_BROWSER="${PLAYWRIGHT_BROWSER}" \
    DOCFLOW_LOGIN_USER=head \
    DOCFLOW_LOGIN_PASSWORD=test2026 \
    ONLYOFFICE_ITEM_PATH=25-18 \
    ONLYOFFICE_EXPECT_DOCUMENT_TYPE=cell \
    node "${ROOT_DIR}/ops/onlyoffice_browser_e2e.mjs"
  run_step "sidebar_ui_audit" env \
    PLAYWRIGHT_BROWSER="${PLAYWRIGHT_BROWSER}" \
    node "${ROOT_DIR}/ops/sidebar_ui_audit.mjs"

  if [ "${RUN_DEEP_AUDIT}" = "1" ]; then
    run_step "deep_module_browser_audit" env \
      PLAYWRIGHT_BROWSER=chromium \
      node "${ROOT_DIR}/ops/deep_module_browser_audit.mjs"
  fi
else
  echo "[day1-week1] playwright runtime not found, skipping browser checks"
fi

cat > "${OUT_DIR}/summary.txt" <<EOF
generated_at=$(date -Iseconds)
browser=${PLAYWRIGHT_BROWSER}
deep_audit=${RUN_DEEP_AUDIT}
reports_dir=${OUT_DIR}
word_scenario=doctor -> 25-14 -> ONLYOFFICE documenteditor
excel_scenario=head -> 25-18 -> ONLYOFFICE spreadsheeteditor
playwright_available=$(have_playwright_runtime && echo 1 || echo 0)
EOF

echo
echo "[day1-week1] acceptance passed"
echo "[day1-week1] reports: ${OUT_DIR}"
