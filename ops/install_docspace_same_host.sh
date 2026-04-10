#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ROOT_DIR="$(docflow_default_root "${SCRIPT_DIR}")"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

HOST="${DOCFLOW_ACCESS_HOST:-${GATEWAY_SERVER_NAME:-}}"
PORT="${DOCFLOW_DOCSPACE_INTERNAL_PORT:-19001}"
DOCS_ORIGIN_HOST="$(docflow_detect_primary_ipv4 || true)"
DOCS_ORIGIN_HOST="${DOCS_ORIGIN_HOST:-${DOCFLOW_ACCESS_HOST:-${GATEWAY_SERVER_NAME:-127.0.0.1}}}"
DOCS_URL="http://${DOCS_ORIGIN_HOST}:${ONLYOFFICE_BIND_PORT:-18083}/"
JWT_SECRET="${ONLYOFFICE_JWT_SECRET:-}"
EXTRA_HOSTS="host.docker.internal:host-gateway"
SKIP_HARDWARE_CHECK="false"
INSTALLER_DIR="${ROOT_DIR}/ops/vendor/onlyoffice-installers/docspace"
DOCSPACE_VOLUMES_DIR="$(docflow_docspace_volumes_dir "${ROOT_DIR}")"

usage() {
  cat <<'EOF'
Usage:
  sudo bash ops/install_docspace_same_host.sh [options]

Options:
  --host <dns-or-ip>          Public host or IP users use for DocFlow
  --port <port>               Internal DocSpace port on this host (default: 19001)
  --docs-url <url>            Existing ONLYOFFICE Docs URL for DocSpace (default: http://host.docker.internal:18083/)
  --jwt-secret <secret>       Existing ONLYOFFICE Docs JWT secret
  --skip-hardware-check       Skip official installer hardware guard
  --installer-dir <path>      Directory with downloaded official installer scripts
  -h, --help                  Show help
EOF
}

fail() {
  echo "[docspace-install] ERROR: $*" >&2
  exit 1
}

require_root() {
  [ "$(id -u)" -eq 0 ] || fail "root is required; run with sudo"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --host)
      HOST="${2:-}"
      shift 2
      ;;
    --port)
      PORT="${2:-}"
      shift 2
      ;;
    --docs-url)
      DOCS_URL="${2:-}"
      shift 2
      ;;
    --jwt-secret)
      JWT_SECRET="${2:-}"
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
[ -n "${HOST}" ] || fail "host is empty"
[ -n "${DOCS_URL}" ] || fail "docs url is empty"
[ -n "${JWT_SECRET}" ] || fail "jwt secret is empty"

if [ ! -x "${INSTALLER_DIR}/docspace-install.sh" ] || [ ! -x "${INSTALLER_DIR}/install-Docker.sh" ] || [ ! -x "${INSTALLER_DIR}/install-Docker-args.sh" ]; then
  bash "${ROOT_DIR}/ops/download_onlyoffice_installers.sh"
fi

echo "[docspace-install] host=${HOST}"
echo "[docspace-install] port=${PORT}"
echo "[docspace-install] docs_url=${DOCS_URL}"
echo "[docspace-install] installer_dir=${INSTALLER_DIR}"
if [ -n "${DOCSPACE_VOLUMES_DIR}" ]; then
  mkdir -p "${DOCSPACE_VOLUMES_DIR}"
  echo "[docspace-install] data_root volumes_dir=${DOCSPACE_VOLUMES_DIR}"
fi

cd "${INSTALLER_DIR}"
INSTALL_ARGS=(
  docker
  -ls true
  -noni true
  -it community
  -dsh "${HOST}"
  -ep "${PORT}"
  -idocs false
  -docsurl "${DOCS_URL}"
  -js "${JWT_SECRET}"
  -eh "${EXTRA_HOSTS}"
  -skiphc "${SKIP_HARDWARE_CHECK}"
)
if [ -n "${DOCSPACE_VOLUMES_DIR}" ]; then
  INSTALL_ARGS+=(-vd "${DOCSPACE_VOLUMES_DIR}")
fi

bash ./docspace-install.sh "${INSTALL_ARGS[@]}"

RUNTIME_DIR="${INSTALLER_DIR}/runtime"
if [ -f "${RUNTIME_DIR}/.env" ]; then
  python3 - "${RUNTIME_DIR}/.env" "${HOST}" "${PORT}" <<'PY'
from pathlib import Path
import sys

env_path = Path(sys.argv[1])
host = sys.argv[2].strip()
port = sys.argv[3].strip()
text = env_path.read_text()

lines = []
replaced_base = False
replaced_portal = False
for line in text.splitlines():
    stripped = line.lstrip()
    if stripped.startswith("APP_CORE_BASE_DOMAIN="):
        indent = line[: len(line) - len(stripped)]
        line = f"{indent}APP_CORE_BASE_DOMAIN={host}"
        replaced_base = True
    elif stripped.startswith("APP_URL_PORTAL="):
        indent = line[: len(line) - len(stripped)]
        line = f"{indent}APP_URL_PORTAL=http://{host}:{port}"
        replaced_portal = True
    lines.append(line)

if not replaced_base:
    lines.append(f"APP_CORE_BASE_DOMAIN={host}")
if not replaced_portal:
    lines.append(f"APP_URL_PORTAL=http://{host}:{port}")

env_path.write_text("\n".join(lines) + "\n")
PY
fi

echo "[docspace-install] repair tenant quota/bootstrap state"
bash "${ROOT_DIR}/ops/repair_docspace_same_host.sh"
