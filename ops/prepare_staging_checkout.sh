#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
LEGACY_HELPER_IMAGE="${NAUDOC_LEGACY_IMAGE:-docflow/naudoc-legacy:local}"

FORCE_ENV=0
TARGET_ROOT=""

for arg in "$@"; do
  case "${arg}" in
    --force-env)
      FORCE_ENV=1
      ;;
    --help|-h)
      echo "usage: bash ops/prepare_staging_checkout.sh [target-root] [--force-env]"
      exit 0
      ;;
    *)
      if [ -z "${TARGET_ROOT}" ]; then
        TARGET_ROOT="${arg}"
      else
        echo "[prepare-staging] unknown argument: ${arg}" >&2
        exit 1
      fi
      ;;
  esac
done

TARGET_ROOT="${TARGET_ROOT:-${DOCFLOW_PROJECT_ROOT:-${ROOT_DIR}-staging}}"

clear_target_root() {
  if [ ! -d "${TARGET_ROOT}" ]; then
    return 0
  fi

  if find "${TARGET_ROOT}" -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null; then
    return 0
  fi

  if ! command -v docker >/dev/null 2>&1; then
    echo "[prepare-staging] cannot clear ${TARGET_ROOT}: permission denied and docker is unavailable" >&2
    return 1
  fi

  docker run --rm --entrypoint bash -u 0:0 -v "${TARGET_ROOT}:/workspace" "${LEGACY_HELPER_IMAGE}" -lc "find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf {} +" >/dev/null
}

if [ "${TARGET_ROOT}" = "${ROOT_DIR}" ]; then
  echo "[prepare-staging] target root must differ from the current project root" >&2
  exit 1
fi

PRESERVE_ENV=0
ENV_SNAPSHOT=""
if [ -f "${TARGET_ROOT}/.env" ] && [ "${FORCE_ENV}" != "1" ]; then
  ENV_SNAPSHOT="$(mktemp)"
  cp "${TARGET_ROOT}/.env" "${ENV_SNAPSHOT}"
  PRESERVE_ENV=1
fi

mkdir -p "${TARGET_ROOT}"
clear_target_root

if [ "${PRESERVE_ENV}" = "1" ] && [ -n "${ENV_SNAPSHOT}" ]; then
  cp "${ENV_SNAPSHOT}" "${TARGET_ROOT}/.env"
  rm -f "${ENV_SNAPSHOT}"
fi

echo "[prepare-staging] syncing project into ${TARGET_ROOT}"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete \
    --exclude='.git/' \
    --exclude='.env' \
    --exclude='.env.generated.*' \
    --exclude='__pycache__/' \
    --exclude='node_modules/' \
    --exclude='ops/node_modules/' \
    --exclude='.tmp_e2e/' \
    --exclude='backups/' \
    --exclude='runtime/portable-bundles/' \
    --exclude='middleware/runtime/' \
    --exclude='rukovoditel-test/dist/cache/' \
    --exclude='rukovoditel-test/dist/log/' \
    "${ROOT_DIR}/" "${TARGET_ROOT}/"
else
  find "${TARGET_ROOT}" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
  (
    cd "${ROOT_DIR}"
    tar \
      --exclude='.git' \
      --exclude='.env' \
      --exclude='.env.generated.*' \
      --exclude='__pycache__' \
      --exclude='node_modules' \
      --exclude='ops/node_modules' \
      --exclude='.tmp_e2e' \
      --exclude='backups' \
      --exclude='runtime/portable-bundles' \
      --exclude='middleware/runtime' \
      --exclude='rukovoditel-test/dist/cache' \
      --exclude='rukovoditel-test/dist/log' \
      -cf - .
  ) | (
    cd "${TARGET_ROOT}"
    tar -xf -
  )
fi

if [ -f "${TARGET_ROOT}/.env" ] && [ "${FORCE_ENV}" != "1" ]; then
  echo "[prepare-staging] keeping existing staging env: ${TARGET_ROOT}/.env"
else
  echo "[prepare-staging] generating staging env"
  DOCFLOW_PROJECT_ROOT="${TARGET_ROOT}" bash "${TARGET_ROOT}/ops/generate_staging_env.sh" "${TARGET_ROOT}/.env"
fi

echo "[prepare-staging] done"
echo "[prepare-staging] next step:"
echo "  bash ${TARGET_ROOT}/ops/start_staging_stack.sh ${TARGET_ROOT} --with-local-ldap"
