#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

WITH_LOCAL_LDAP=0
BUILD_MODE="build"
TARGET_ROOT="${DOCFLOW_PROJECT_ROOT:-${ROOT_DIR}-staging}"

ARGS=()
for arg in "$@"; do
  case "${arg}" in
    --with-local-ldap)
      WITH_LOCAL_LDAP=1
      ;;
    --no-build)
      BUILD_MODE="no-build"
      ;;
    --*)
      echo "[start-staging] unknown argument: ${arg}" >&2
      exit 1
      ;;
    *)
      TARGET_ROOT="${arg}"
      ;;
  esac
done

if [ ! -d "${TARGET_ROOT}" ]; then
  echo "[start-staging] staging root does not exist: ${TARGET_ROOT}" >&2
  echo "[start-staging] create a separate staging checkout first." >&2
  exit 1
fi

if [ ! -f "${TARGET_ROOT}/.env" ]; then
  echo "[start-staging] missing ${TARGET_ROOT}/.env" >&2
  echo "[start-staging] generate staging env and place it as .env inside the staging checkout." >&2
  exit 1
fi

if [ "${WITH_LOCAL_LDAP}" = "1" ]; then
  ARGS+=("--with-local-ldap")
fi

if [ "${BUILD_MODE}" = "no-build" ]; then
  ARGS+=("--no-build")
fi

DOCFLOW_ENV_FILE="${TARGET_ROOT}/.env" bash "${TARGET_ROOT}/ops/start_stack.sh" "${ARGS[@]}"
