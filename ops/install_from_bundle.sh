#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TARGET_ROOT="${1:-/opt/docflow}"
WITH_LOCAL_LDAP="${DOCFLOW_WITH_LOCAL_LDAP:-0}"

if [ -f "${SCRIPT_DIR}/config/bundle.flags" ] && grep -q '^WITH_LOCAL_LDAP=1$' "${SCRIPT_DIR}/config/bundle.flags"; then
  WITH_LOCAL_LDAP=1
fi

ARTIFACTS_DIR="${SCRIPT_DIR}/artifacts"
PROJECT_ARCHIVE="${ARTIFACTS_DIR}/project.tar.gz"
BACKUP_ARCHIVE="${ARTIFACTS_DIR}/backup.tar.gz"
IMAGES_ARCHIVE="${ARTIFACTS_DIR}/docker-images.tar"
ENV_SOURCE="${SCRIPT_DIR}/config/.env"

for required in "${PROJECT_ARCHIVE}" "${BACKUP_ARCHIVE}" "${IMAGES_ARCHIVE}" "${ENV_SOURCE}"; do
  if [ ! -f "${required}" ]; then
    echo "[install] missing bundle file: ${required}" >&2
    exit 1
  fi
done

if [ -d "${TARGET_ROOT}" ] && [ -n "$(find "${TARGET_ROOT}" -mindepth 1 -maxdepth 1 2>/dev/null | head -n 1)" ]; then
  echo "[install] target directory is not empty: ${TARGET_ROOT}" >&2
  echo "[install] use an empty path, for example /opt/docflow" >&2
  exit 1
fi

mkdir -p "${TARGET_ROOT}"

echo "[install] extract project to ${TARGET_ROOT}"
tar -xzf "${PROJECT_ARCHIVE}" -C "${TARGET_ROOT}"

echo "[install] install env"
install -m 600 "${ENV_SOURCE}" "${TARGET_ROOT}/.env"

echo "[install] load docker images"
docker load -i "${IMAGES_ARCHIVE}"

echo "[install] unpack backup snapshot"
mkdir -p "${TARGET_ROOT}/runtime/install-bundle/backup"
tar -xzf "${BACKUP_ARCHIVE}" -C "${TARGET_ROOT}/runtime/install-bundle/backup"

cd "${TARGET_ROOT}"

echo "[install] start MariaDB and app containers"
docker compose --project-directory "${TARGET_ROOT}/rukovoditel-test" -p "$(grep '^RUKOVODITEL_COMPOSE_PROJECT_NAME=' .env | cut -d= -f2-)" --env-file .env -f rukovoditel-test/docker-compose.yml up -d --no-build rukovoditel_db rukovoditel onlyoffice_docs rukovoditel_sync_worker
docker compose --project-directory "${TARGET_ROOT}/middleware" -p "$(grep '^MIDDLEWARE_COMPOSE_PROJECT_NAME=' .env | cut -d= -f2-)" --env-file .env -f middleware/docker-compose.yml up -d --no-build middleware
docker compose --project-directory "${TARGET_ROOT}" -p "$(grep '^NAUDOC_LEGACY_COMPOSE_PROJECT=' .env | cut -d= -f2-)" --env-file .env -f docker-compose.legacy.yml up -d --no-build naudoc_legacy
docker compose --project-directory "${TARGET_ROOT}/gateway" --env-file .env -f gateway/docker-compose.yml up -d --no-build gateway

echo "[install] restore data snapshot"
bash ops/restore_all.sh "${TARGET_ROOT}/runtime/install-bundle/backup"

if [ "${WITH_LOCAL_LDAP}" = "1" ]; then
  echo "[install] enable local ldap baseline"
  docker compose --project-directory "${TARGET_ROOT}/middleware" -p "$(grep '^MIDDLEWARE_COMPOSE_PROJECT_NAME=' .env | cut -d= -f2-)" --env-file .env -f middleware/docker-compose.yml --profile identity up -d --no-build hospital_ldap
  bash ops/bootstrap_local_ldap.sh
fi

echo "[install] post-install check"
bash ops/check_stack.sh

echo "[install] done"
echo "[install] platform: https://$(grep '^GATEWAY_SERVER_NAME=' .env | cut -d= -f2-)/"
echo "[install] next step: bash ops/smoke_test_stack.sh"
