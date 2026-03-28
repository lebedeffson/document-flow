#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"
# shellcheck source=lib/compose_stack.sh
source "${SCRIPT_DIR}/lib/compose_stack.sh"

docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

ENV_FILE="$(docflow_env_file_path "${ROOT_DIR}")"
WITH_LOCAL_LDAP=0
BUILD_MODE="build"

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

docflow_stack_up "${ROOT_DIR}" "${ENV_FILE}" "${BUILD_MODE}" "${WITH_LOCAL_LDAP}"

if [ "${WITH_LOCAL_LDAP}" = "1" ]; then
  DOCFLOW_ENV_FILE="${ENV_FILE}" bash "${ROOT_DIR}/ops/bootstrap_local_ldap.sh"
fi

bash "${ROOT_DIR}/ops/check_stack.sh"

echo "[start-stack] done"
echo "[start-stack] platform: ${DOCFLOW_PUBLIC_BASE}/"
