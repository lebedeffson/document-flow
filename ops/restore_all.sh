#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/home/lebedeffson/Code/Документооборот"
BACKUP_DIR="${1:-}"

if [ -z "${BACKUP_DIR}" ]; then
  echo "Usage: $0 /path/to/backup-dir" >&2
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

RESTORE_STAMP="$(date +%Y%m%d-%H%M%S)"

echo "[restore] restoring MariaDB"
docker exec rukovoditel_db_test sh -lc \
  "mariadb -uroot -proot_rukovoditel -e 'DROP DATABASE IF EXISTS rukovoditel; CREATE DATABASE rukovoditel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; GRANT ALL PRIVILEGES ON rukovoditel.* TO \"rukovoditel\"@\"%\"; FLUSH PRIVILEGES;'"
docker exec -i rukovoditel_db_test sh -lc \
  'exec mariadb -urukovoditel -prukovoditel rukovoditel' \
  < "${SQL_FILE}"

echo "[restore] restoring bridge.db"
docker exec naudoc_bridge_test sh -lc \
  "if [ -f /data/bridge.db ]; then cp /data/bridge.db /data/bridge.db.before-restore.${RESTORE_STAMP}; fi"
docker cp "${BRIDGE_FILE}" naudoc_bridge_test:/data/bridge.db

echo "[restore] restoring NauDoc Data.fs"
docker compose --project-directory "${ROOT_DIR}" -p naudoclegacy -f "${ROOT_DIR}/docker-compose.legacy.yml" stop naudoc_legacy >/dev/null
if [ -f "${ROOT_DIR}/naudoc_project/var/Data.fs" ]; then
  cp "${ROOT_DIR}/naudoc_project/var/Data.fs" "${ROOT_DIR}/naudoc_project/var/Data.fs.before-restore.${RESTORE_STAMP}"
fi
cp "${DATA_FS_FILE}" "${ROOT_DIR}/naudoc_project/var/Data.fs"
docker compose --project-directory "${ROOT_DIR}" -p naudoclegacy -f "${ROOT_DIR}/docker-compose.legacy.yml" up -d naudoc_legacy >/dev/null

echo "[restore] done"
