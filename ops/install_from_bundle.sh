#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

TARGET_ROOT="/opt/docflow"
DATA_ROOT="${DOCFLOW_DATA_ROOT:-}"
WITH_LOCAL_LDAP="${DOCFLOW_WITH_LOCAL_LDAP:-0}"
VERIFY_ONLY="${DOCFLOW_VERIFY_ONLY:-0}"

if [ -f "${SCRIPT_DIR}/config/bundle.flags" ] && grep -q '^WITH_LOCAL_LDAP=1$' "${SCRIPT_DIR}/config/bundle.flags"; then
  WITH_LOCAL_LDAP=1
fi

ARTIFACTS_DIR="${SCRIPT_DIR}/artifacts"
PROJECT_ARCHIVE="${ARTIFACTS_DIR}/project.tar.gz"
BACKUP_ARCHIVE="${ARTIFACTS_DIR}/backup.tar.gz"
IMAGES_ARCHIVE="${ARTIFACTS_DIR}/docker-images.tar"
ENV_SOURCE="${SCRIPT_DIR}/config/.env"
CHECKSUM_FILE="${SCRIPT_DIR}/SHA256SUMS"

while [ $# -gt 0 ]; do
  case "$1" in
    --data-root)
      DATA_ROOT="${2:-}"
      shift 2
      ;;
    *)
      TARGET_ROOT="$1"
      shift
      ;;
  esac
done

fail() {
  echo "[install] ERROR: $*" >&2
  exit 1
}

require_command() {
  local command_name="${1:-}"
  command -v "${command_name}" >/dev/null 2>&1 || fail "required command is missing: ${command_name}"
}

run_prod_readiness_preflight() {
  local target_root="${1:-}"
  local env_file="${2:-}"
  local output_file="${3:-}"

  if ! command -v python3 >/dev/null 2>&1; then
    echo "[install] python3 not found, skipping production readiness preflight"
    return 0
  fi

  echo "[install] production readiness preflight"
  DOCFLOW_ENV_FILE="${env_file}" python3 "${target_root}/ops/prod_readiness_audit.py" | tee "${output_file}"

  python3 - "${output_file}" <<'PY'
import json
import pathlib
import sys

report_path = pathlib.Path(sys.argv[1])
raw = report_path.read_text(encoding="utf-8")
start = raw.find("{")
end = raw.rfind("}")
if start == -1 or end == -1 or end < start:
    print("[install] could not parse production readiness report", file=sys.stderr)
    sys.exit(1)
report = json.loads(raw[start:end + 1])
blocker_count = int(report.get("blocker_count", 0))
warning_count = int(report.get("warning_count", 0))

if blocker_count:
    print(f"[install] production readiness blockers: {blocker_count}", file=sys.stderr)
    for item in report.get("blockers", []):
        print(f"[install] blocker: {item}", file=sys.stderr)
    sys.exit(1)

print("[install] production readiness blockers: 0")
if warning_count:
    print(f"[install] production readiness warnings: {warning_count}")
    for item in report.get("warnings", []):
        print(f"[install] warning: {item}")
else:
    print("[install] production readiness warnings: 0")
PY
}

for required in "${PROJECT_ARCHIVE}" "${BACKUP_ARCHIVE}" "${IMAGES_ARCHIVE}" "${ENV_SOURCE}"; do
  if [ ! -f "${required}" ]; then
    fail "missing bundle file: ${required}"
  fi
done

require_command docker
docker compose version >/dev/null 2>&1 || fail "docker compose is required"
require_command tar
require_command bash

if [ -f "${CHECKSUM_FILE}" ] && command -v sha256sum >/dev/null 2>&1; then
  echo "[install] verify bundle checksums"
  (
    cd "${SCRIPT_DIR}"
    sha256sum -c SHA256SUMS
  )
fi

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

if [ -n "${DATA_ROOT}" ]; then
  docflow_configure_data_root_env "${TARGET_ROOT}/.env" "${DATA_ROOT}"
fi

echo "[install] detect access host and normalize public URLs"
DOCFLOW_ENV_FILE="${TARGET_ROOT}/.env" bash "${TARGET_ROOT}/ops/configure_access_host.sh"

docflow_load_env "${TARGET_ROOT}"
docflow_prepare_host_storage

mkdir -p "${TARGET_ROOT}/runtime/install-bundle"
run_prod_readiness_preflight "${TARGET_ROOT}" "${TARGET_ROOT}/.env" "${TARGET_ROOT}/runtime/install-bundle/preinstall_prod_readiness.json"

if [ "${VERIFY_ONLY}" = "1" ]; then
  echo "[install] verify-only complete; bundle, env, extraction and readiness preflight passed"
  exit 0
fi

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
DOCFLOW_ENV_FILE="${TARGET_ROOT}/.env" bash ops/show_access_points.sh

echo "[install] done"
echo "[install] platform: $(grep '^RUKOVODITEL_PUBLIC_URL=' .env | cut -d= -f2-)/"
echo "[install] next step: bash ops/smoke_test_stack.sh"
