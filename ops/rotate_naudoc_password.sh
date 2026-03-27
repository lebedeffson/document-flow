#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ROOT_DIR="${PROJECT_ROOT:-$(docflow_default_root "${SCRIPT_DIR}")}"
ENV_FILE="$(docflow_env_file_path "${ROOT_DIR}")"
docflow_load_env "${ROOT_DIR}"
ROOT_DIR="${PROJECT_ROOT:-${ROOT_DIR}}"
docflow_export_runtime

if [ ! -f "${ENV_FILE}" ]; then
  echo "[rotate-naudoc] missing env file: ${ENV_FILE}" >&2
  exit 1
fi

USERNAME="${NAUDOC_USERNAME:-admin}"
CURRENT_PASSWORD="${NAUDOC_PASSWORD:-}"
NEW_PASSWORD="${1:-$(docflow_random_secret 24)}"
VERIFY_URL="${DOCFLOW_DOCS_BASE}/manage_users_form"
CHANGE_URL="${DOCFLOW_DOCS_BASE}/change_password"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="${ROOT_DIR}/backups/pre-naudoc-password-rotation-${STAMP}"
ENV_BACKUP_FILE="${BACKUP_DIR}/env/.env.before"

PASSWORD_ROTATED=0
ENV_UPDATED=0
SERVICES_RESTARTED=0

verify_credentials() {
  local username="${1}"
  local password="${2}"
  local code
  code="$(curl -k -s -o /dev/null -w '%{http_code}' -u "${username}:${password}" "${VERIFY_URL}" || true)"
  [ "${code}" = "200" ]
}

change_password() {
  local current_password="${1}"
  local target_password="${2}"
  local output_file
  output_file="$(mktemp)"
  local code
  code="$(
    curl -k -s -o "${output_file}" -w '%{http_code}' \
      -u "${USERNAME}:${current_password}" \
      -X POST "${CHANGE_URL}" \
      --data-urlencode "userid=${USERNAME}" \
      --data-urlencode "password=${target_password}" \
      --data-urlencode "confirm=${target_password}" \
      || true
  )"

  if [ "${code}" != "200" ]; then
    echo "[rotate-naudoc] password change returned HTTP ${code}" >&2
    rm -f "${output_file}"
    return 1
  fi

  rm -f "${output_file}"
}

recreate_dependents() {
  (
    cd "${ROOT_DIR}"
    docker compose -p "${MIDDLEWARE_COMPOSE_PROJECT_NAME}" -f middleware/docker-compose.yml up -d --no-build --force-recreate middleware >/dev/null
    docker compose -p "${RUKOVODITEL_COMPOSE_PROJECT_NAME}" -f rukovoditel-test/docker-compose.yml up -d --no-build --force-recreate rukovoditel rukovoditel_sync_worker >/dev/null
  )
}

rollback_rotation() {
  echo "[rotate-naudoc] rollback started" >&2

  if [ "${PASSWORD_ROTATED}" = "1" ]; then
    if verify_credentials "${USERNAME}" "${NEW_PASSWORD}"; then
      change_password "${NEW_PASSWORD}" "${CURRENT_PASSWORD}" || true
    fi
  fi

  if [ "${ENV_UPDATED}" = "1" ] && [ -f "${ENV_BACKUP_FILE}" ]; then
    cp "${ENV_BACKUP_FILE}" "${ENV_FILE}" || true
  fi

  if [ "${SERVICES_RESTARTED}" = "1" ] || [ "${ENV_UPDATED}" = "1" ]; then
    docflow_load_env "${ROOT_DIR}"
    docflow_export_runtime
    recreate_dependents || true
  fi
}

trap 'rc=$?; if [ ${rc} -ne 0 ]; then rollback_rotation; fi; exit ${rc}' EXIT

if [ -z "${CURRENT_PASSWORD}" ]; then
  echo "[rotate-naudoc] NAUDOC_PASSWORD is empty in env" >&2
  exit 1
fi

if [ "${CURRENT_PASSWORD}" = "${NEW_PASSWORD}" ]; then
  echo "[rotate-naudoc] new password matches current password; refusing no-op rotation" >&2
  exit 1
fi

if ! verify_credentials "${USERNAME}" "${CURRENT_PASSWORD}"; then
  echo "[rotate-naudoc] current NauDoc credentials are invalid" >&2
  exit 1
fi

mkdir -p "${BACKUP_DIR}/env"
echo "[rotate-naudoc] creating pre-rotation backup: ${BACKUP_DIR}"
bash "${ROOT_DIR}/ops/backup_all.sh" "${BACKUP_DIR}/full-backup" >/dev/null
cp "${ENV_FILE}" "${ENV_BACKUP_FILE}"

echo "[rotate-naudoc] changing NauDoc password"
change_password "${CURRENT_PASSWORD}" "${NEW_PASSWORD}"
PASSWORD_ROTATED=1

if ! verify_credentials "${USERNAME}" "${NEW_PASSWORD}"; then
  echo "[rotate-naudoc] new NauDoc credentials did not verify" >&2
  exit 1
fi

docflow_set_env_value "${ENV_FILE}" "NAUDOC_PASSWORD" "${NEW_PASSWORD}"
ENV_UPDATED=1

docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

echo "[rotate-naudoc] recreating dependent containers"
recreate_dependents
SERVICES_RESTARTED=1

if ! verify_credentials "${USERNAME}" "${NEW_PASSWORD}"; then
  echo "[rotate-naudoc] credentials failed after container recreation" >&2
  exit 1
fi

python3 "${ROOT_DIR}/ops/prod_readiness_audit.py" >/dev/null
echo "[rotate-naudoc] completed successfully"
echo "[rotate-naudoc] env updated: ${ENV_FILE}"
echo "[rotate-naudoc] backup saved: ${BACKUP_DIR}"
