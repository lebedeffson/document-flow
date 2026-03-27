#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ROOT_DIR="${PROJECT_ROOT:-$(docflow_default_root "${SCRIPT_DIR}")}"
docflow_load_env "${ROOT_DIR}"
ROOT_DIR="${PROJECT_ROOT:-${ROOT_DIR}}"

VERIFY_ONLY=0
BACKUP_DIR=""
for arg in "$@"; do
  if [ "${arg}" = "--verify-only" ]; then
    VERIFY_ONLY=1
  elif [ -z "${BACKUP_DIR}" ]; then
    BACKUP_DIR="${arg}"
  else
    echo "Usage: $0 /path/to/backup-dir [--verify-only]" >&2
    exit 1
  fi
done

DB_CONTAINER="${RUKOVODITEL_DB_CONTAINER:-rukovoditel_db_test}"
DB_NAME="${RUKOVODITEL_DB_NAME:-rukovoditel}"
DB_USER="${RUKOVODITEL_DB_USER:-rukovoditel}"
DB_PASSWORD="${RUKOVODITEL_DB_PASSWORD:-rukovoditel}"
DB_ROOT_PASSWORD="${RUKOVODITEL_DB_ROOT_PASSWORD:-root_rukovoditel}"
BRIDGE_CONTAINER="${BRIDGE_CONTAINER:-naudoc_bridge_test}"
NAUDOC_LEGACY_COMPOSE_PROJECT="${NAUDOC_LEGACY_COMPOSE_PROJECT:-naudoclegacy}"
NAUDOC_LEGACY_SERVICE="${NAUDOC_LEGACY_SERVICE:-naudoc_legacy}"
NAUDOC_LEGACY_CONTAINER="${NAUDOC_LEGACY_CONTAINER:-naudoc34_legacy}"

if [ -z "${BACKUP_DIR}" ]; then
  echo "Usage: $0 /path/to/backup-dir [--verify-only]" >&2
  exit 1
fi

SQL_FILE="${BACKUP_DIR}/mariadb/rukovoditel.sql"
BRIDGE_FILE="${BACKUP_DIR}/bridge/bridge.db"
DATA_FS_FILE="${BACKUP_DIR}/naudoc/Data.fs"

for required in "${SQL_FILE}" "${BRIDGE_FILE}" "${DATA_FS_FILE}"; do
  if [ ! -f "${required}" ]; then
    echo "[restore] missing file: ${required}" >&2
    exit 1
  fi
done

docflow_verify_backup_dir "${BACKUP_DIR}"

if [ "${VERIFY_ONLY}" = "1" ]; then
  echo "[restore] backup verification only: ok"
  exit 0
fi

RESTORE_STAMP="$(date +%Y%m%d-%H%M%S)"

stop_naudoc_legacy() {
  if docker compose --project-directory "${ROOT_DIR}" -p "${NAUDOC_LEGACY_COMPOSE_PROJECT}" -f "${ROOT_DIR}/docker-compose.legacy.yml" ps "${NAUDOC_LEGACY_SERVICE}" >/dev/null 2>&1; then
    docker compose --project-directory "${ROOT_DIR}" -p "${NAUDOC_LEGACY_COMPOSE_PROJECT}" -f "${ROOT_DIR}/docker-compose.legacy.yml" stop "${NAUDOC_LEGACY_SERVICE}" >/dev/null 2>&1 || true
  fi

  if docker ps --format '{{.Names}}' | grep -qx "${NAUDOC_LEGACY_CONTAINER}"; then
    docker stop "${NAUDOC_LEGACY_CONTAINER}" >/dev/null
  fi
}

start_naudoc_legacy() {
  if docker ps -a --format '{{.Names}}' | grep -qx "${NAUDOC_LEGACY_CONTAINER}"; then
    docker start "${NAUDOC_LEGACY_CONTAINER}" >/dev/null
    return 0
  fi

  docker compose --project-directory "${ROOT_DIR}" -p "${NAUDOC_LEGACY_COMPOSE_PROJECT}" -f "${ROOT_DIR}/docker-compose.legacy.yml" up -d "${NAUDOC_LEGACY_SERVICE}" >/dev/null
}

echo "[restore] restoring MariaDB"
docker exec "${DB_CONTAINER}" sh -lc \
  "mariadb -uroot -p\"${DB_ROOT_PASSWORD}\" -e 'DROP DATABASE IF EXISTS ${DB_NAME}; CREATE DATABASE ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO \"${DB_USER}\"@\"%\"; FLUSH PRIVILEGES;'"
docker exec -i "${DB_CONTAINER}" sh -lc \
  "exec mariadb -u\"${DB_USER}\" -p\"${DB_PASSWORD}\" \"${DB_NAME}\"" \
  < "${SQL_FILE}"

echo "[restore] restoring bridge.db"
docker exec "${BRIDGE_CONTAINER}" sh -lc \
  "if [ -f /data/bridge.db ]; then cp /data/bridge.db /data/bridge.db.before-restore.${RESTORE_STAMP}; fi"
docker cp "${BRIDGE_FILE}" "${BRIDGE_CONTAINER}:/data/bridge.db"

echo "[restore] restoring NauDoc Data.fs"
stop_naudoc_legacy
if [ -f "${ROOT_DIR}/naudoc_project/var/Data.fs" ]; then
  cp "${ROOT_DIR}/naudoc_project/var/Data.fs" "${ROOT_DIR}/naudoc_project/var/Data.fs.before-restore.${RESTORE_STAMP}"
fi
cp "${DATA_FS_FILE}" "${ROOT_DIR}/naudoc_project/var/Data.fs"
start_naudoc_legacy

echo "[restore] done"
