#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TARGET_ROOT="/opt/docflow"
WORKSPACE_SCOPE=""
SKIP_VERIFY=0
WITH_LIVE_OFFICE=0
OFFICE_AUTO_HOST=0
OFFICE_HOST=""
DOCSPACE_PORT=""
WORKSPACE_PORT=""
SKIP_OFFICE_HARDWARE_CHECK=0

usage() {
  cat <<'EOF'
Usage:
  bash install_everything.sh [options] [target-root]

Options:
  --with-live-office           Install live DocSpace + Workspace on the same host after base install
  --office-host <dns-or-ip>    Public host/IP for the live office same-host cutover
  --office-auto-host           Auto-detect the primary IPv4 for the live office same-host cutover
  --docspace-port <port>       Internal DocSpace port for same-host live mode
  --workspace-port <port>      Internal Workspace port for same-host live mode
  --workspace-with-community   Keep Calendar and expose Community
  --workspace-calendar-only    Keep only Calendar in Workspace Wave 1
  --skip-office-hardware-check Pass through skip flag to official live office installers
  --skip-verify                Skip post-install Python audits
  -h, --help                   Show this help

Defaults:
  target-root: /opt/docflow
  workspace scope: calendar-only
EOF
}

fail() {
  echo "[install-everything] ERROR: $*" >&2
  exit 1
}

env_value() {
  local key="${1:-}"
  local file="${2:-.env}"

  if [ ! -f "${file}" ]; then
    return 0
  fi

  grep "^${key}=" "${file}" | tail -n 1 | cut -d= -f2-
}

ensure_command() {
  local command_name="${1:-}"
  command -v "${command_name}" >/dev/null 2>&1 || fail "required command is missing: ${command_name}"
}

require_root_if_needed() {
  if [ "${WITH_LIVE_OFFICE}" = "1" ] && [ "$(id -u)" -ne 0 ]; then
    fail "--with-live-office requires root; rerun as sudo bash install_everything.sh ..."
  fi
}

run_prod_readiness_check() {
  local target_root="${1:-}"
  local env_file="${2:-}"
  local output_file="${3:-}"

  if ! command -v python3 >/dev/null 2>&1; then
    echo "[install-everything] python3 not found, skipping production readiness verification"
    return 0
  fi

  echo "[install-everything] production readiness verification"
  DOCFLOW_ENV_FILE="${env_file}" python3 "${target_root}/ops/prod_readiness_audit.py" | tee "${output_file}"

  python3 - "${output_file}" <<'PY'
import json
import pathlib
import sys

report_path = pathlib.Path(sys.argv[1])
report = json.loads(report_path.read_text(encoding="utf-8"))
blocker_count = int(report.get("blocker_count", 0))
warning_count = int(report.get("warning_count", 0))

if blocker_count:
    print(f"[install-everything] production readiness blockers: {blocker_count}", file=sys.stderr)
    for item in report.get("blockers", []):
        print(f"[install-everything] blocker: {item}", file=sys.stderr)
    sys.exit(1)

print("[install-everything] production readiness blockers: 0")
if warning_count:
    print(f"[install-everything] production readiness warnings: {warning_count}")
    for item in report.get("warnings", []):
        print(f"[install-everything] warning: {item}")
else:
    print("[install-everything] production readiness warnings: 0")
PY
}

verify_bundle_checksums() {
  if [ ! -f "${SCRIPT_DIR}/SHA256SUMS" ]; then
    echo "[install-everything] SHA256SUMS not found, skipping checksum verification"
    return 0
  fi

  if ! command -v sha256sum >/dev/null 2>&1; then
    echo "[install-everything] sha256sum not found, skipping checksum verification"
    return 0
  fi

  echo "[install-everything] verify bundle checksums"
  (
    cd "${SCRIPT_DIR}"
    sha256sum -c SHA256SUMS
  )
}

while [ $# -gt 0 ]; do
  case "$1" in
    --workspace-with-community)
      WORKSPACE_SCOPE="with_community"
      ;;
    --workspace-calendar-only)
      WORKSPACE_SCOPE="calendar_only"
      ;;
    --with-live-office)
      WITH_LIVE_OFFICE=1
      ;;
    --office-host)
      OFFICE_HOST="${2:-}"
      shift
      ;;
    --office-auto-host)
      OFFICE_AUTO_HOST=1
      ;;
    --docspace-port)
      DOCSPACE_PORT="${2:-}"
      shift
      ;;
    --workspace-port)
      WORKSPACE_PORT="${2:-}"
      shift
      ;;
    --skip-office-hardware-check)
      SKIP_OFFICE_HARDWARE_CHECK=1
      ;;
    --skip-verify)
      SKIP_VERIFY=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      TARGET_ROOT="$1"
      ;;
  esac
  shift
done

ensure_command docker
docker compose version >/dev/null 2>&1 || fail "docker compose is required"
ensure_command tar
ensure_command bash
require_root_if_needed

if [ ! -f "${SCRIPT_DIR}/install_from_bundle.sh" ]; then
  fail "install_from_bundle.sh not found next to install_everything.sh"
fi

verify_bundle_checksums

echo "[install-everything] target root: ${TARGET_ROOT}"
echo "[install-everything] bundle dir: ${SCRIPT_DIR}"

bash "${SCRIPT_DIR}/install_from_bundle.sh" "${TARGET_ROOT}"

cd "${TARGET_ROOT}"

if [ -z "${WORKSPACE_SCOPE}" ]; then
  if [ "$(env_value DOCFLOW_WORKSPACE_WAVE1_ENABLE_COMMUNITY .env)" = "1" ]; then
    WORKSPACE_SCOPE="with_community"
  else
    WORKSPACE_SCOPE="calendar_only"
  fi
fi

OFFICE_ARGS=()

DOCSPACE_TARGET_URL_VALUE="$(env_value DOCSPACE_TARGET_URL .env)"
WORKSPACE_TARGET_URL_VALUE="$(env_value WORKSPACE_TARGET_URL .env)"
DOCSPACE_COLLABORATION_TARGET_URL_VALUE="$(env_value DOCSPACE_COLLABORATION_ROOM_TARGET_URL .env)"
DOCSPACE_PUBLIC_TARGET_URL_VALUE="$(env_value DOCSPACE_PUBLIC_ROOM_TARGET_URL .env)"
DOCSPACE_FORM_FILLING_TARGET_URL_VALUE="$(env_value DOCSPACE_FORM_FILLING_ROOM_TARGET_URL .env)"
WORKSPACE_CALENDAR_TARGET_URL_VALUE="$(env_value WORKSPACE_CALENDAR_TARGET_URL .env)"
WORKSPACE_COMMUNITY_TARGET_URL_VALUE="$(env_value WORKSPACE_COMMUNITY_TARGET_URL .env)"
REQUIRE_LIVE_TARGETS_VALUE="$(env_value DOCFLOW_OFFICE_WAVE1_REQUIRE_LIVE_TARGETS .env)"

if [ -n "${DOCSPACE_TARGET_URL_VALUE}" ]; then
  OFFICE_ARGS+=(--docspace-target "${DOCSPACE_TARGET_URL_VALUE}")
else
  OFFICE_ARGS+=(--docspace-shell-only)
fi

if [ -n "${WORKSPACE_TARGET_URL_VALUE}" ]; then
  OFFICE_ARGS+=(--workspace-target "${WORKSPACE_TARGET_URL_VALUE}")
else
  OFFICE_ARGS+=(--workspace-shell-only)
fi

if [ -n "${DOCSPACE_COLLABORATION_TARGET_URL_VALUE}" ]; then
  OFFICE_ARGS+=(--docspace-collaboration-target "${DOCSPACE_COLLABORATION_TARGET_URL_VALUE}")
fi

if [ -n "${DOCSPACE_PUBLIC_TARGET_URL_VALUE}" ]; then
  OFFICE_ARGS+=(--docspace-public-target "${DOCSPACE_PUBLIC_TARGET_URL_VALUE}")
fi

if [ -n "${DOCSPACE_FORM_FILLING_TARGET_URL_VALUE}" ]; then
  OFFICE_ARGS+=(--docspace-form-filling-target "${DOCSPACE_FORM_FILLING_TARGET_URL_VALUE}")
fi

if [ -n "${WORKSPACE_CALENDAR_TARGET_URL_VALUE}" ]; then
  OFFICE_ARGS+=(--workspace-calendar-target "${WORKSPACE_CALENDAR_TARGET_URL_VALUE}")
fi

if [ -n "${WORKSPACE_COMMUNITY_TARGET_URL_VALUE}" ]; then
  OFFICE_ARGS+=(--workspace-community-target "${WORKSPACE_COMMUNITY_TARGET_URL_VALUE}")
fi

if [ "${WORKSPACE_SCOPE}" = "with_community" ]; then
  OFFICE_ARGS+=(--workspace-with-community)
else
  OFFICE_ARGS+=(--workspace-calendar-only)
fi

if [ "${REQUIRE_LIVE_TARGETS_VALUE:-0}" = "1" ]; then
  OFFICE_ARGS+=(--require-live-targets)
else
  OFFICE_ARGS+=(--allow-shell-only)
fi

echo "[install-everything] configure Office Wave 1"
bash ops/configure_office_wave1.sh "${OFFICE_ARGS[@]}"

mkdir -p runtime/monitoring
run_prod_readiness_check "${TARGET_ROOT}" "${TARGET_ROOT}/.env" "${TARGET_ROOT}/runtime/monitoring/install_prod_readiness.json"

echo "[install-everything] restart stack with final env"
bash ops/start_stack.sh --no-build

if [ "${WITH_LIVE_OFFICE}" = "1" ]; then
  if command -v python3 >/dev/null 2>&1; then
    echo "[install-everything] office same-host host audit"
    python3 ops/office_wave1_host_audit.py | tee runtime/monitoring/install_office_host_audit.json || true
  fi

  LIVE_OFFICE_ARGS=()
  if [ -n "${OFFICE_HOST}" ]; then
    LIVE_OFFICE_ARGS+=(--host "${OFFICE_HOST}")
  elif [ "${OFFICE_AUTO_HOST}" = "1" ]; then
    LIVE_OFFICE_ARGS+=(--auto-host)
  fi

  if [ -n "${DOCSPACE_PORT}" ]; then
    LIVE_OFFICE_ARGS+=(--docspace-port "${DOCSPACE_PORT}")
  fi

  if [ -n "${WORKSPACE_PORT}" ]; then
    LIVE_OFFICE_ARGS+=(--workspace-port "${WORKSPACE_PORT}")
  fi

  if [ "${WORKSPACE_SCOPE}" = "with_community" ]; then
    LIVE_OFFICE_ARGS+=(--workspace-with-community)
  else
    LIVE_OFFICE_ARGS+=(--workspace-calendar-only)
  fi

  if [ "${SKIP_OFFICE_HARDWARE_CHECK}" = "1" ]; then
    LIVE_OFFICE_ARGS+=(--skip-hardware-check)
  fi

  echo "[install-everything] install live Office layer"
  bash ops/install_office_live_same_host.sh "${LIVE_OFFICE_ARGS[@]}"
fi

if [ "${SKIP_VERIFY}" != "1" ] && command -v python3 >/dev/null 2>&1; then
  echo "[install-everything] monitoring snapshot"
  python3 ops/monitoring_snapshot.py | tee runtime/monitoring/install_monitoring_snapshot.txt

  echo "[install-everything] ecosystem audit"
  python3 ops/audit_ecosystem_integration.py | tee runtime/monitoring/install_ecosystem_audit.txt
else
  echo "[install-everything] python3 not found or verification skipped, skipping Python audits"
fi

if [ "${WITH_LIVE_OFFICE}" = "1" ] && [ "${SKIP_VERIFY}" != "1" ] && command -v node >/dev/null 2>&1; then
  echo "[install-everything] live office auth"
  node ops/audit_live_office_auth.mjs | tee runtime/monitoring/install_live_office_auth.txt
fi

echo "[install-everything] export quick start"
bash ops/export_server_quickstart.sh >/dev/null

cat > runtime/monitoring/install_everything_summary.txt <<EOF
installed_at=$(date -Iseconds)
target_root=${TARGET_ROOT}
workspace_scope=${WORKSPACE_SCOPE}
with_live_office=${WITH_LIVE_OFFICE}
office_host=${OFFICE_HOST}
office_auto_host=${OFFICE_AUTO_HOST}
docspace_port=${DOCSPACE_PORT}
workspace_port=${WORKSPACE_PORT}
skip_office_hardware_check=${SKIP_OFFICE_HARDWARE_CHECK}
docspace_target_url=$(env_value DOCSPACE_TARGET_URL .env)
workspace_target_url=$(env_value WORKSPACE_TARGET_URL .env)
docspace_collaboration_target_url=$(env_value DOCSPACE_COLLABORATION_ROOM_TARGET_URL .env)
docspace_public_target_url=$(env_value DOCSPACE_PUBLIC_ROOM_TARGET_URL .env)
docspace_form_filling_target_url=$(env_value DOCSPACE_FORM_FILLING_ROOM_TARGET_URL .env)
workspace_calendar_target_url=$(env_value WORKSPACE_CALENDAR_TARGET_URL .env)
workspace_community_target_url=$(env_value WORKSPACE_COMMUNITY_TARGET_URL .env)
docflow_public_url=$(env_value RUKOVODITEL_PUBLIC_URL .env)
access_points_file=${TARGET_ROOT}/runtime/monitoring/access_points.txt
quick_start_file=${TARGET_ROOT}/runtime/monitoring/START_HERE.txt
EOF

echo
echo "[install-everything] completed"
echo "[install-everything] open: $(env_value RUKOVODITEL_PUBLIC_URL .env)/"
echo "[install-everything] access points: ${TARGET_ROOT}/runtime/monitoring/access_points.txt"
echo "[install-everything] quick start: ${TARGET_ROOT}/runtime/monitoring/START_HERE.txt"
echo "[install-everything] summary: ${TARGET_ROOT}/runtime/monitoring/install_everything_summary.txt"
cat "${TARGET_ROOT}/runtime/monitoring/START_HERE.txt"
