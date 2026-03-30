#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: bash rukovoditel-test/import_hospital_users.sh /path/to/users.csv [--update-passwords]" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../ops/lib/runtime_env.sh
source "${ROOT_DIR}/ops/lib/runtime_env.sh"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

CSV_PATH="$1"
shift || true

if [ ! -f "${CSV_PATH}" ]; then
  echo "CSV file not found: ${CSV_PATH}" >&2
  exit 1
fi

CONTAINER_CSV_PATH="/tmp/docflow_hospital_users_import.csv"

docker cp "${CSV_PATH}" "${RUKOVODITEL_CONTAINER_NAME}:${CONTAINER_CSV_PATH}"
trap 'docker exec "${RUKOVODITEL_CONTAINER_NAME}" rm -f "'"${CONTAINER_CSV_PATH}"'" >/dev/null 2>&1 || true' EXIT

docker exec \
  -e DOCFLOW_ADMIN_PASSWORD="${DOCFLOW_ADMIN_PASSWORD}" \
  -e DOCFLOW_ROLE_DEFAULT_PASSWORD="${DOCFLOW_ROLE_DEFAULT_PASSWORD}" \
  -e DOCFLOW_HOSPITAL_USER_DEFAULT_PASSWORD="${DOCFLOW_HOSPITAL_USER_DEFAULT_PASSWORD:-${DOCFLOW_ROLE_DEFAULT_PASSWORD}}" \
  -e BRIDGE_BASE_URL="${BRIDGE_BASE_URL}" \
  -e DOCFLOW_PUBLIC_BASE="${DOCFLOW_PUBLIC_BASE}" \
  -e RUKOVODITEL_PUBLIC_URL="${RUKOVODITEL_PUBLIC_URL}" \
  "${RUKOVODITEL_CONTAINER_NAME}" php /var/www/html/scripts/import_hospital_users.php "${CONTAINER_CSV_PATH}" "$@"
