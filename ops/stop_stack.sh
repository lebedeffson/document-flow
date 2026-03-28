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
WITH_LOCAL_LDAP=1

for arg in "$@"; do
  case "${arg}" in
    --without-ldap)
      WITH_LOCAL_LDAP=0
      ;;
    *)
      echo "[stop-stack] unknown argument: ${arg}" >&2
      exit 1
      ;;
  esac
done

if [ ! -f "${ENV_FILE}" ]; then
  echo "[stop-stack] missing env file: ${ENV_FILE}" >&2
  exit 1
fi

docflow_stack_down "${ROOT_DIR}" "${ENV_FILE}" "${WITH_LOCAL_LDAP}"
echo "[stop-stack] done"
