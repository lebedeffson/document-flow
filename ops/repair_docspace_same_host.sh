#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ROOT_DIR="$(docflow_default_root "${SCRIPT_DIR}")"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

API_CONTAINER="${DOCSPACE_API_CONTAINER_NAME:-onlyoffice-api}"
DB_CONTAINER="${DOCSPACE_DB_CONTAINER_NAME:-onlyoffice-mysql-server}"
DB_NAME="${DOCSPACE_DB_NAME:-docspace}"
WAIT_SECONDS=120

usage() {
  cat <<'EOF'
Usage:
  bash ops/repair_docspace_same_host.sh [options]

Options:
  --api-container <name>  DocSpace API container name (default: onlyoffice-api)
  --db-container <name>   DocSpace MySQL container name (default: onlyoffice-mysql-server)
  --db-name <name>        DocSpace database name (default: docspace)
  --wait-seconds <sec>    Wait timeout after API restart (default: 120)
  -h, --help              Show help
EOF
}

fail() {
  echo "[docspace-repair] ERROR: $*" >&2
  exit 1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --api-container)
      API_CONTAINER="${2:-}"
      shift 2
      ;;
    --db-container)
      DB_CONTAINER="${2:-}"
      shift 2
      ;;
    --db-name)
      DB_NAME="${2:-}"
      shift 2
      ;;
    --wait-seconds)
      WAIT_SECONDS="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown option: $1"
      ;;
  esac
done

[[ "${WAIT_SECONDS}" =~ ^[0-9]+$ ]] || fail "invalid wait timeout: ${WAIT_SECONDS}"
docker inspect "${DB_CONTAINER}" >/dev/null 2>&1 || fail "db container not found: ${DB_CONTAINER}"
docker inspect "${API_CONTAINER}" >/dev/null 2>&1 || fail "api container not found: ${API_CONTAINER}"

MYSQL_ROOT_PASSWORD="$(
  docker inspect "${DB_CONTAINER}" --format '{{range .Config.Env}}{{println .}}{{end}}' \
    | awk -F= '/^MYSQL_ROOT_PASSWORD=/{sub(/^MYSQL_ROOT_PASSWORD=/,""); print; exit}'
)"
[ -n "${MYSQL_ROOT_PASSWORD}" ] || fail "could not detect MYSQL_ROOT_PASSWORD from ${DB_CONTAINER}"

read -r -d '' SQL <<'EOF' || true
INSERT INTO tenants_quota (tenant, name, description, features, price, product_id, visible, wallet, service_name)
SELECT
  t.id,
  CONCAT('tenant-', t.id),
  q.description,
  q.features,
  q.price,
  q.product_id,
  q.visible,
  q.wallet,
  q.service_name
FROM tenants_tenants t
JOIN tenants_quota q ON q.tenant = -1
LEFT JOIN tenants_quota existing ON existing.tenant = t.id
WHERE t.id <> -1
  AND existing.tenant IS NULL;
SELECT tenant, name FROM tenants_quota ORDER BY tenant;
EOF

echo "[docspace-repair] ensure tenant quota rows in ${DB_NAME}"
docker exec "${DB_CONTAINER}" mysql -uroot "-p${MYSQL_ROOT_PASSWORD}" -D "${DB_NAME}" -e "${SQL}"

echo "[docspace-repair] restart ${API_CONTAINER}"
docker restart "${API_CONTAINER}" >/dev/null

echo "[docspace-repair] wait for internal API"
for _ in $(seq 1 "${WAIT_SECONDS}"); do
  if docker exec "${API_CONTAINER}" sh -lc "python3 - <<'PY'
import sys
import urllib.request

try:
    with urllib.request.urlopen('http://127.0.0.1:5050/api/2.0/settings/ssov2', timeout=5) as response:
        sys.exit(0 if int(getattr(response, 'status', 500)) < 400 else 1)
except Exception:
    sys.exit(1)
PY" >/dev/null 2>&1; then
    echo "[docspace-repair] internal API is healthy"
    exit 0
  fi
  sleep 1
done

fail "DocSpace API did not become ready in ${WAIT_SECONDS}s"
