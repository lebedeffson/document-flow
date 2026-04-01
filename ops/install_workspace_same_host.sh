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
LOW_MEMORY_PROFILE="false"
INSTALLER_DIR="${ROOT_DIR}/ops/vendor/onlyoffice-installers/workspace"
WORKSPACE_BASE_DIR="$(docflow_workspace_base_dir "${ROOT_DIR}")"
INSTALLER_RUN_DIR=""
TEMP_INSTALLER_DIR=""

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
  --low-memory-profile        Recreate Elasticsearch in a reduced profile for ~16 GB hosts
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

prepare_workspace_installer_dir() {
  local source_dir="${1:-}"

  [ -d "${source_dir}" ] || fail "workspace installer dir not found: ${source_dir}"

  if [ -z "${WORKSPACE_BASE_DIR}" ]; then
    printf '%s\n' "${source_dir}"
    return 0
  fi

  mkdir -p "${WORKSPACE_BASE_DIR}"
  TEMP_INSTALLER_DIR="$(mktemp -d)"
  cp -a "${source_dir}/." "${TEMP_INSTALLER_DIR}/"

  python3 - "${TEMP_INSTALLER_DIR}/install.sh" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
needle = 'BASE_DIR="/app/$PRODUCT";'
replacement = 'BASE_DIR="${WORKSPACE_BASE_DIR:-/app/$PRODUCT}";'

if needle not in text:
    raise SystemExit(f"workspace installer patch target not found in {path}")

path.write_text(text.replace(needle, replacement, 1), encoding="utf-8")
PY

  printf '%s\n' "${TEMP_INSTALLER_DIR}"
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
    --low-memory-profile)
      LOW_MEMORY_PROFILE="true"
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

trap 'if [ -n "${TEMP_INSTALLER_DIR}" ] && [ -d "${TEMP_INSTALLER_DIR}" ]; then rm -rf "${TEMP_INSTALLER_DIR}"; fi' EXIT
INSTALLER_RUN_DIR="$(prepare_workspace_installer_dir "${INSTALLER_DIR}")"

echo "[workspace-install] port=${PORT}"
echo "[workspace-install] docs_host=${DOCS_HOST}"
echo "[workspace-install] installer_dir=${INSTALLER_DIR}"
if [ -n "${WORKSPACE_BASE_DIR}" ]; then
  echo "[workspace-install] data_root workspace_base_dir=${WORKSPACE_BASE_DIR}"
fi

cd "${INSTALLER_RUN_DIR}"
WORKSPACE_BASE_DIR="${WORKSPACE_BASE_DIR}" bash ./workspace-install.sh \
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

TUNE_ARGS=()
if [ "${LOW_MEMORY_PROFILE}" = "true" ]; then
  TUNE_ARGS+=(--low-memory-profile)
fi

echo "[workspace-install] tune Elasticsearch/runtime profile"
bash "${ROOT_DIR}/ops/tune_workspace_same_host.sh" "${TUNE_ARGS[@]}"
