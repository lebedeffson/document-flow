#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/home/lebedeffson/Code/Документооборот"
STAMP="$(date +%Y%m%d-%H%M%S)"
TARGET_DIR="${1:-${ROOT_DIR}/backups/${STAMP}}"

mkdir -p "${TARGET_DIR}/mariadb" "${TARGET_DIR}/bridge" "${TARGET_DIR}/naudoc"

echo "[backup] target: ${TARGET_DIR}"

echo "[backup] dumping MariaDB"
docker exec rukovoditel_db_test sh -lc \
  'exec mariadb-dump -urukovoditel -prukovoditel --single-transaction --routines --events rukovoditel' \
  > "${TARGET_DIR}/mariadb/rukovoditel.sql"

echo "[backup] copying bridge.db"
docker cp naudoc_bridge_test:/data/bridge.db "${TARGET_DIR}/bridge/bridge.db"

echo "[backup] copying NauDoc Data.fs"
cp "${ROOT_DIR}/naudoc_project/var/Data.fs" "${TARGET_DIR}/naudoc/Data.fs"

cat > "${TARGET_DIR}/manifest.txt" <<EOF
created_at=${STAMP}
source_root=${ROOT_DIR}
containers=rukovoditel_db_test,naudoc_bridge_test,naudoc34_legacy
files=
  mariadb/rukovoditel.sql
  bridge/bridge.db
  naudoc/Data.fs
EOF

if command -v sha256sum >/dev/null 2>&1; then
  (
    cd "${TARGET_DIR}"
    sha256sum mariadb/rukovoditel.sql bridge/bridge.db naudoc/Data.fs > SHA256SUMS
  )
fi

echo "[backup] done"
