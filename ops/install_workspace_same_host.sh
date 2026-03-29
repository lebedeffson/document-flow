#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ROOT_DIR="$(docflow_default_root "${SCRIPT_DIR}")"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

PORT="${DOCFLOW_WORKSPACE_INTERNAL_PORT:-19002}"
DOCS_HOST="host.docker.internal:${ONLYOFFICE_BIND_PORT:-18083}"
JWT_SECRET="${ONLYOFFICE_JWT_SECRET:-}"
JWT_HEADER="Authorization"
SKIP_HARDWARE_CHECK="false"
INSTALLER_DIR="${ROOT_DIR}/ops/vendor/onlyoffice-installers/workspace"

usage() {
  cat <<'EOF'
Usage:
  sudo bash ops/install_workspace_same_host.sh [options]

Options:
  --port <port>               Internal Workspace port on this host (default: 19002)
  --docs-host <host[:port]>   Existing ONLYOFFICE Docs host for external Document Server
  --jwt-secret <secret>       Existing ONLYOFFICE Docs JWT secret
  --jwt-header <header>       JWT header for existing ONLYOFFICE Docs (default: Authorization)
  --skip-hardware-check       Skip official installer hardware guard
  --installer-dir <path>      Directory with downloaded official installer scripts
  -h, --help                  Show help
EOF
}

fail() {
  echo "[workspace-install] ERROR: $*" >&2
  exit 1
}

require_root() {
  [ "$(id -u)" -eq 0 ] || fail "root is required; run with sudo"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --port)
      PORT="${2:-}"
      shift 2
      ;;
    --docs-host)
      DOCS_HOST="${2:-}"
      shift 2
      ;;
    --jwt-secret)
      JWT_SECRET="${2:-}"
      shift 2
      ;;
    --jwt-header)
      JWT_HEADER="${2:-}"
      shift 2
      ;;
    --installer-dir)
      INSTALLER_DIR="${2:-}"
      shift 2
      ;;
    --skip-hardware-check)
      SKIP_HARDWARE_CHECK="true"
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

[[ "${PORT}" =~ ^[0-9]+$ ]] || fail "invalid port: ${PORT}"
[ -n "${DOCS_HOST}" ] || fail "docs host is empty"
[ -n "${JWT_SECRET}" ] || fail "jwt secret is empty"
[ -n "${JWT_HEADER}" ] || fail "jwt header is empty"

if [ ! -x "${INSTALLER_DIR}/workspace-install.sh" ] || [ ! -x "${INSTALLER_DIR}/install.sh" ]; then
  bash "${ROOT_DIR}/ops/download_onlyoffice_installers.sh"
fi

echo "[workspace-install] port=${PORT}"
echo "[workspace-install] docs_host=${DOCS_HOST}"
echo "[workspace-install] installer_dir=${INSTALLER_DIR}"

cd "${INSTALLER_DIR}"
bash ./workspace-install.sh \
  -ls true \
  -ics true \
  -icp true \
  -ids false \
  -ims false \
  -es true \
  -dip "${DOCS_HOST}" \
  -cp "${PORT}" \
  -je true \
  -jh "${JWT_HEADER}" \
  -js "${JWT_SECRET}" \
  -skiphc "${SKIP_HARDWARE_CHECK}"
