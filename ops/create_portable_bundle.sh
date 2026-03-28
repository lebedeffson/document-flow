#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ROOT_DIR="$(docflow_default_root "${SCRIPT_DIR}")"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

VERIFY_ONLY=0
WITH_LOCAL_LDAP=0
OUTPUT_DIR=""

while [ $# -gt 0 ]; do
  case "$1" in
    --verify-only)
      VERIFY_ONLY=1
      shift
      ;;
    --with-local-ldap)
      WITH_LOCAL_LDAP=1
      shift
      ;;
    *)
      if [ -n "${OUTPUT_DIR}" ]; then
        echo "Usage: $0 [--verify-only] [--with-local-ldap] [output-dir]" >&2
        exit 1
      fi
      OUTPUT_DIR="$1"
      shift
      ;;
  esac
done

ENV_FILE="$(docflow_env_file_path "${ROOT_DIR}")"
if [ ! -f "${ENV_FILE}" ]; then
  echo "[bundle] missing env file: ${ENV_FILE}" >&2
  exit 1
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
OUTPUT_DIR="${OUTPUT_DIR:-${ROOT_DIR}/runtime/portable-bundles/docflow-portable-${STAMP}}"
BACKUP_DIR="${ROOT_DIR}/backups/portable-bundle-${STAMP}"

REQUIRED_IMAGES=(
  "${GATEWAY_IMAGE}"
  "${BRIDGE_IMAGE}"
  "${RUKOVODITEL_APP_IMAGE}"
  "${NAUDOC_LEGACY_IMAGE}"
  "${MARIADB_IMAGE}"
  "${ONLYOFFICE_IMAGE}"
)

if [ "${WITH_LOCAL_LDAP}" = "1" ]; then
  REQUIRED_IMAGES+=("${LDAP_IMAGE}")
fi

echo "[bundle] env: ${ENV_FILE}"
echo "[bundle] root: ${ROOT_DIR}"

echo "[bundle] build local images"
docker compose --project-directory "${ROOT_DIR}/gateway" --env-file "${ENV_FILE}" -f "${ROOT_DIR}/gateway/docker-compose.yml" build gateway
docker compose --project-directory "${ROOT_DIR}/middleware" -p "${MIDDLEWARE_COMPOSE_PROJECT_NAME}" --env-file "${ENV_FILE}" -f "${ROOT_DIR}/middleware/docker-compose.yml" build middleware
docker compose --project-directory "${ROOT_DIR}/rukovoditel-test" -p "${RUKOVODITEL_COMPOSE_PROJECT_NAME}" --env-file "${ENV_FILE}" -f "${ROOT_DIR}/rukovoditel-test/docker-compose.yml" build rukovoditel rukovoditel_sync_worker
docker compose --project-directory "${ROOT_DIR}" -p "${NAUDOC_LEGACY_COMPOSE_PROJECT}" --env-file "${ENV_FILE}" -f "${ROOT_DIR}/docker-compose.legacy.yml" build naudoc_legacy

for image in "${REQUIRED_IMAGES[@]}"; do
  docker image inspect "${image}" >/dev/null
done

if [ ! -d "${ROOT_DIR}/ops/node_modules/playwright" ]; then
  echo "[bundle] bootstrap ops node_modules"
  npm install --prefix "${ROOT_DIR}/ops" --no-fund --no-audit
fi

if [ "${VERIFY_ONLY}" = "1" ]; then
  echo "[bundle] verify-only: ready for portable bundle creation"
  printf '[bundle] images:\n'
  printf '  %s\n' "${REQUIRED_IMAGES[@]}"
  exit 0
fi

mkdir -p "${OUTPUT_DIR}/artifacts" "${OUTPUT_DIR}/config"

echo "[bundle] backup snapshot"
bash "${ROOT_DIR}/ops/backup_all.sh" "${BACKUP_DIR}"

echo "[bundle] save docker images"
docker save -o "${OUTPUT_DIR}/artifacts/docker-images.tar" "${REQUIRED_IMAGES[@]}"

echo "[bundle] pack project"
tar -C "${ROOT_DIR}" -czf "${OUTPUT_DIR}/artifacts/project.tar.gz" \
  --exclude='.git' \
  --exclude='.env' \
  --exclude='.env.*' \
  --exclude='.tmp_e2e' \
  --exclude='backups' \
  --exclude='runtime/portable-bundles' \
  --exclude='runtime/monitoring' \
  --exclude='runtime/ldap' \
  --exclude='middleware/runtime' \
  --exclude='__pycache__' \
  --exclude='*/__pycache__' \
  --exclude='rukovoditel-test/dist/cache' \
  --exclude='rukovoditel-test/dist/log' \
  --exclude='rukovoditel-test/dist/uploads' \
  .

echo "[bundle] pack backup snapshot"
tar -C "${BACKUP_DIR}" -czf "${OUTPUT_DIR}/artifacts/backup.tar.gz" .

echo "[bundle] copy env"
install -m 600 "${ENV_FILE}" "${OUTPUT_DIR}/config/.env"

echo "[bundle] copy installer"
install -m 755 "${ROOT_DIR}/ops/install_from_bundle.sh" "${OUTPUT_DIR}/install_from_bundle.sh"

if [ "${WITH_LOCAL_LDAP}" = "1" ]; then
  printf 'WITH_LOCAL_LDAP=1\n' > "${OUTPUT_DIR}/config/bundle.flags"
else
  : > "${OUTPUT_DIR}/config/bundle.flags"
fi

cat > "${OUTPUT_DIR}/BUNDLE_MANIFEST.txt" <<EOF
created_at=${STAMP}
source_root=${ROOT_DIR}
env_file=${ENV_FILE}
with_local_ldap=${WITH_LOCAL_LDAP}
artifacts=
  artifacts/project.tar.gz
  artifacts/backup.tar.gz
  artifacts/docker-images.tar
  config/.env
  install_from_bundle.sh
images=
$(printf '  %s\n' "${REQUIRED_IMAGES[@]}")
EOF

if command -v sha256sum >/dev/null 2>&1; then
  (
    cd "${OUTPUT_DIR}"
    sha256sum artifacts/project.tar.gz artifacts/backup.tar.gz artifacts/docker-images.tar config/.env install_from_bundle.sh > SHA256SUMS
  )
fi

echo "[bundle] ready: ${OUTPUT_DIR}"
echo "[bundle] install on target: bash install_from_bundle.sh /opt/docflow"
