#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

TARGET_ROOT="${DOCFLOW_PROJECT_ROOT:-${ROOT_DIR}-staging}"

for arg in "$@"; do
  case "${arg}" in
    --*)
      echo "[stop-staging] unknown argument: ${arg}" >&2
      exit 1
      ;;
    *)
      TARGET_ROOT="${arg}"
      ;;
  esac
done

if [ ! -d "${TARGET_ROOT}" ]; then
  echo "[stop-staging] staging root does not exist: ${TARGET_ROOT}" >&2
  exit 1
fi

if [ ! -f "${TARGET_ROOT}/.env" ]; then
  echo "[stop-staging] missing ${TARGET_ROOT}/.env" >&2
  exit 1
fi

DOCFLOW_ENV_FILE="${TARGET_ROOT}/.env" bash "${TARGET_ROOT}/ops/stop_stack.sh"
