#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ROOT_DIR="${PROJECT_ROOT:-$(docflow_default_root "${SCRIPT_DIR}")}"
docflow_load_env "${ROOT_DIR}"
ROOT_DIR="${PROJECT_ROOT:-${ROOT_DIR}}"
STAMP="$(date +%Y%m%d-%H%M%S)"
TARGET_DIR="${1:-${ROOT_DIR}/backups/${STAMP}}"
DB_CONTAINER="${RUKOVODITEL_DB_CONTAINER:-rukovoditel_db_test}"
DB_NAME="${RUKOVODITEL_DB_NAME:-rukovoditel}"
DB_USER="${RUKOVODITEL_DB_USER:-rukovoditel}"
DB_PASSWORD="${RUKOVODITEL_DB_PASSWORD:-rukovoditel}"
BRIDGE_CONTAINER="${BRIDGE_CONTAINER:-naudoc_bridge_test}"
NAUDOC_LEGACY_CONTAINER="${NAUDOC_LEGACY_CONTAINER:-naudoc34_legacy}"

mkdir -p "${TARGET_DIR}/mariadb" "${TARGET_DIR}/bridge" "${TARGET_DIR}/naudoc"

echo "[backup] target: ${TARGET_DIR}"

echo "[backup] dumping MariaDB"
docker exec "${DB_CONTAINER}" sh -lc \
  "exec mariadb-dump -u\"${DB_USER}\" -p\"${DB_PASSWORD}\" --single-transaction --routines --events \"${DB_NAME}\"" \
  > "${TARGET_DIR}/mariadb/rukovoditel.sql"

echo "[backup] copying bridge.db"
docker cp "${BRIDGE_CONTAINER}:/data/bridge.db" "${TARGET_DIR}/bridge/bridge.db"

echo "[backup] copying NauDoc Data.fs"
cp "${ROOT_DIR}/naudoc_project/var/Data.fs" "${TARGET_DIR}/naudoc/Data.fs"

cat > "${TARGET_DIR}/manifest.txt" <<EOF
created_at=${STAMP}
source_root=${ROOT_DIR}
containers=${DB_CONTAINER},${BRIDGE_CONTAINER},${NAUDOC_LEGACY_CONTAINER}
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
