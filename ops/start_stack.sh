#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"
# shellcheck source=lib/compose_stack.sh
source "${SCRIPT_DIR}/lib/compose_stack.sh"

ENV_FILE="$(docflow_env_file_path "${ROOT_DIR}")"
WITH_LOCAL_LDAP=0
BUILD_MODE="build"
CHECK_ATTEMPTS="${DOCFLOW_START_STACK_CHECK_ATTEMPTS:-12}"
CHECK_SLEEP_SECONDS="${DOCFLOW_START_STACK_CHECK_SLEEP_SECONDS:-5}"

for arg in "$@"; do
  case "${arg}" in
    --with-local-ldap)
      WITH_LOCAL_LDAP=1
      ;;
    --no-build)
      BUILD_MODE="no-build"
      ;;
    *)
      echo "[start-stack] unknown argument: ${arg}" >&2
      exit 1
      ;;
  esac
done

if [ ! -f "${ENV_FILE}" ]; then
  echo "[start-stack] missing env file: ${ENV_FILE}" >&2
  exit 1
fi

DOCFLOW_ENV_FILE="${ENV_FILE}" bash "${ROOT_DIR}/ops/configure_access_host.sh"

docflow_load_env "${ROOT_DIR}"
docflow_export_runtime
docflow_prepare_host_storage

docflow_stack_up "${ROOT_DIR}" "${ENV_FILE}" "${BUILD_MODE}" "${WITH_LOCAL_LDAP}"

if [ "${WITH_LOCAL_LDAP}" = "1" ]; then
  DOCFLOW_ENV_FILE="${ENV_FILE}" bash "${ROOT_DIR}/ops/bootstrap_local_ldap.sh"
fi

attempt=1
while true; do
  if bash "${ROOT_DIR}/ops/check_stack.sh"; then
    break
  fi

  if [ "${attempt}" -ge "${CHECK_ATTEMPTS}" ]; then
    echo "[start-stack] check_stack failed after ${attempt} attempts" >&2
    exit 1
  fi

  echo "[start-stack] check_stack not ready yet, retry ${attempt}/${CHECK_ATTEMPTS} after ${CHECK_SLEEP_SECONDS}s" >&2
  sleep "${CHECK_SLEEP_SECONDS}"
  attempt=$((attempt + 1))
done

DOCFLOW_ENV_FILE="${ENV_FILE}" bash "${ROOT_DIR}/ops/show_access_points.sh"

echo "[start-stack] done"
echo "[start-stack] platform: ${DOCFLOW_PUBLIC_BASE}/"
