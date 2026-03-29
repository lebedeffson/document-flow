#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ROOT_DIR="$(docflow_default_root "${SCRIPT_DIR}")"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

HOST="${DOCFLOW_ACCESS_HOST:-${GATEWAY_SERVER_NAME:-}}"
AUTO_HOST=0
DOCSPACE_PORT="${DOCFLOW_DOCSPACE_INTERNAL_PORT:-19001}"
WORKSPACE_PORT="${DOCFLOW_WORKSPACE_INTERNAL_PORT:-19002}"
WORKSPACE_SCOPE="calendar_only"
SKIP_HARDWARE_CHECK=0

usage() {
  cat <<'EOF'
Usage:
  sudo bash ops/install_office_live_same_host.sh [options]

Options:
  --host <dns-or-ip>          Public host or IP for DocFlow
  --auto-host                 Detect the primary IPv4 and use it as the public host
  --docspace-port <port>      Internal DocSpace port (default: 19001)
  --workspace-port <port>     Internal Workspace port (default: 19002)
  --workspace-with-community  Expose Workspace Community after cutover
  --workspace-calendar-only   Keep only Calendar in Workspace Wave 1 (default)
  --skip-hardware-check       Pass through skip flag to official ONLYOFFICE installers
  -h, --help                  Show help
EOF
}

fail() {
  echo "[office-live-install] ERROR: $*" >&2
  exit 1
}

require_root() {
  [ "$(id -u)" -eq 0 ] || fail "root is required; run with sudo"
}

run_host_preflight() {
  local report_path
  report_path="$(mktemp)"

  if ! command -v python3 >/dev/null 2>&1; then
    echo "[office-live-install] python3 not found; skipping host preflight"
    return 0
  fi

  echo "[office-live-install] host preflight"
  if python3 "${ROOT_DIR}/ops/office_wave1_host_audit.py" > "${report_path}"; then
    cat "${report_path}"
    rm -f "${report_path}"
    return 0
  fi

  cat "${report_path}"

  if [ "${SKIP_HARDWARE_CHECK}" = "1" ]; then
    echo "[office-live-install] continuing despite host preflight failure because --skip-hardware-check is enabled"
    rm -f "${report_path}"
    return 0
  fi

  rm -f "${report_path}"
  fail "host is not ready for combined same-host DocSpace + Workspace; rerun with --skip-hardware-check only if you explicitly accept the risk"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --host)
      HOST="${2:-}"
      shift 2
      ;;
    --auto-host)
      AUTO_HOST=1
      shift
      ;;
    --docspace-port)
      DOCSPACE_PORT="${2:-}"
      shift 2
      ;;
    --workspace-port)
      WORKSPACE_PORT="${2:-}"
      shift 2
      ;;
    --workspace-with-community)
      WORKSPACE_SCOPE="with_community"
      shift
      ;;
    --workspace-calendar-only)
      WORKSPACE_SCOPE="calendar_only"
      shift
      ;;
    --skip-hardware-check)
      SKIP_HARDWARE_CHECK=1
      shift
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

require_root

if [ "${AUTO_HOST}" = "1" ]; then
  HOST="$(docflow_detect_primary_ipv4 || true)"
fi

[ -n "${HOST}" ] || fail "host is empty"
[[ "${DOCSPACE_PORT}" =~ ^[0-9]+$ ]] || fail "invalid docspace port: ${DOCSPACE_PORT}"
[[ "${WORKSPACE_PORT}" =~ ^[0-9]+$ ]] || fail "invalid workspace port: ${WORKSPACE_PORT}"

run_host_preflight

bash "${ROOT_DIR}/ops/download_onlyoffice_installers.sh"

DOCSPACE_ARGS=(--host "${HOST}" --port "${DOCSPACE_PORT}")
WORKSPACE_ARGS=(--port "${WORKSPACE_PORT}")
if [ "${SKIP_HARDWARE_CHECK}" = "1" ]; then
  DOCSPACE_ARGS+=(--skip-hardware-check)
  WORKSPACE_ARGS+=(--skip-hardware-check)
fi

echo "[office-live-install] install DocSpace"
bash "${ROOT_DIR}/ops/install_docspace_same_host.sh" "${DOCSPACE_ARGS[@]}"

echo "[office-live-install] install Workspace"
bash "${ROOT_DIR}/ops/install_workspace_same_host.sh" "${WORKSPACE_ARGS[@]}"

CUTOVER_ARGS=(--host "${HOST}" --docspace-port "${DOCSPACE_PORT}" --workspace-port "${WORKSPACE_PORT}")
if [ "${WORKSPACE_SCOPE}" = "with_community" ]; then
  CUTOVER_ARGS+=(--workspace-with-community)
else
  CUTOVER_ARGS+=(--workspace-calendar-only)
fi

echo "[office-live-install] cutover DocFlow"
bash "${ROOT_DIR}/ops/cutover_closed_lan_prod.sh" "${CUTOVER_ARGS[@]}"
