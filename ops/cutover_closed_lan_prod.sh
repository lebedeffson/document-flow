#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ENV_FILE="$(docflow_env_file_path "${ROOT_DIR}")"
ACCESS_HOST_ARG=""
AUTO_HOST=0
DOCSPACE_PORT="${DOCFLOW_DOCSPACE_INTERNAL_PORT:-19001}"
WORKSPACE_PORT="${DOCFLOW_WORKSPACE_INTERNAL_PORT:-19002}"
WORKSPACE_SCOPE="calendar_only"
RUN_STACK_CHECKS=1
OFFICE_MODE="same_host_proxy"

usage() {
  cat <<'EOF'
Usage:
  bash ops/cutover_closed_lan_prod.sh [options]

Options:
  --host <dns-or-ip>            Set final public host or IP for the gateway
  --auto-host                   Detect the primary IPv4 and use it as the public host
  --same-host-office            Route DocSpace/Workspace through the same gateway (default)
  --shell-only-office           Keep DocSpace/Workspace in shell-only mode
  --docspace-port <port>        Internal DocSpace upstream port for same-host proxy mode
  --workspace-port <port>       Internal Workspace upstream port for same-host proxy mode
  --workspace-calendar-only     Keep Workspace Wave 1 in Calendar-only mode (default)
  --workspace-with-community    Expose Workspace Community in Wave 1
  --skip-stack-checks           Do not restart the stack or run live checks after env update
  --env-file <path>             Use a specific env file instead of the default .env
  -h, --help                    Show this help

Examples:
  bash ops/cutover_closed_lan_prod.sh --auto-host
  bash ops/cutover_closed_lan_prod.sh --host 172.16.10.20
  bash ops/cutover_closed_lan_prod.sh --host docflow.hospital.local --workspace-with-community
EOF
}

fail() {
  echo "[cutover] ERROR: $*" >&2
  exit 1
}

while [ "$#" -gt 0 ]; do
  case "${1}" in
    --host)
      ACCESS_HOST_ARG="${2:-}"
      shift 2
      ;;
    --host=*)
      ACCESS_HOST_ARG="${1#*=}"
      shift
      ;;
    --auto-host)
      AUTO_HOST=1
      shift
      ;;
    --same-host-office)
      OFFICE_MODE="same_host_proxy"
      shift
      ;;
    --shell-only-office)
      OFFICE_MODE="shell_only"
      shift
      ;;
    --docspace-port)
      DOCSPACE_PORT="${2:-}"
      shift 2
      ;;
    --docspace-port=*)
      DOCSPACE_PORT="${1#*=}"
      shift
      ;;
    --workspace-port)
      WORKSPACE_PORT="${2:-}"
      shift 2
      ;;
    --workspace-port=*)
      WORKSPACE_PORT="${1#*=}"
      shift
      ;;
    --workspace-calendar-only)
      WORKSPACE_SCOPE="calendar_only"
      shift
      ;;
    --workspace-with-community)
      WORKSPACE_SCOPE="with_community"
      shift
      ;;
    --skip-stack-checks)
      RUN_STACK_CHECKS=0
      shift
      ;;
    --env-file)
      ENV_FILE="${2:-}"
      shift 2
      ;;
    --env-file=*)
      ENV_FILE="${1#*=}"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown option: ${1}"
      ;;
  esac
done

[ -f "${ENV_FILE}" ] || fail "missing env file: ${ENV_FILE}"
[[ "${DOCSPACE_PORT}" =~ ^[0-9]+$ ]] || fail "invalid docspace port: ${DOCSPACE_PORT}"
[[ "${WORKSPACE_PORT}" =~ ^[0-9]+$ ]] || fail "invalid workspace port: ${WORKSPACE_PORT}"

ACCESS_ARGS=(--env-file "${ENV_FILE}")
if [ -n "${ACCESS_HOST_ARG}" ]; then
  ACCESS_ARGS+=(--host "${ACCESS_HOST_ARG}")
elif [ "${AUTO_HOST}" = "1" ]; then
  ACCESS_ARGS+=(--auto)
fi

echo "[cutover] normalize public access host"
DOCFLOW_ENV_FILE="${ENV_FILE}" bash "${ROOT_DIR}/ops/configure_access_host.sh" "${ACCESS_ARGS[@]}"

OFFICE_ARGS=(--env-file "${ENV_FILE}")

# configure_office_wave1.sh reads DOCFLOW_ENV_FILE; keep argument parity by exporting it.
export DOCFLOW_ENV_FILE="${ENV_FILE}"

if [ "${OFFICE_MODE}" = "same_host_proxy" ]; then
  OFFICE_ARGS=(
    --docspace-target "http://host.docker.internal:${DOCSPACE_PORT}/"
    --workspace-target "http://host.docker.internal:${WORKSPACE_PORT}/"
    --require-live-targets
  )
else
  OFFICE_ARGS=(
    --docspace-shell-only
    --workspace-shell-only
    --allow-shell-only
  )
fi

if [ "${WORKSPACE_SCOPE}" = "with_community" ]; then
  OFFICE_ARGS+=(--workspace-with-community)
else
  OFFICE_ARGS+=(--workspace-calendar-only)
fi

echo "[cutover] configure Office Wave 1"
bash "${ROOT_DIR}/ops/configure_office_wave1.sh" "${OFFICE_ARGS[@]}"

echo "[cutover] production readiness"
DOCFLOW_ENV_FILE="${ENV_FILE}" python3 "${ROOT_DIR}/ops/prod_readiness_audit.py"

if [ "${RUN_STACK_CHECKS}" = "1" ]; then
  echo "[cutover] restart stack"
  DOCFLOW_ENV_FILE="${ENV_FILE}" bash "${ROOT_DIR}/ops/start_stack.sh" --no-build

  echo "[cutover] monitoring snapshot"
  DOCFLOW_ENV_FILE="${ENV_FILE}" python3 "${ROOT_DIR}/ops/monitoring_snapshot.py"
fi

echo "[cutover] done"
echo "[cutover] env file: ${ENV_FILE}"
