#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ROOT_DIR="$(docflow_default_root "${SCRIPT_DIR}")"
TARGET_ROOT="${ROOT_DIR}"
INSTALL_PREREQS=0
WITH_LOCAL_LDAP=1
WITH_LIVE_OFFICE=0
OFFICE_AUTO_HOST=0
OFFICE_HOST=""
DOCSPACE_PORT=""
WORKSPACE_PORT=""
WORKSPACE_SCOPE="calendar_only"
SKIP_OFFICE_HARDWARE_CHECK=0
GENERATE_SIMPLE_PASSWORDS=0
REGENERATE_ENV=0
VERIFY_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  bash ops/install_from_git.sh [options]

По умолчанию сценарий ставит платформу прямо в текущем git checkout.

Options:
  --install-prereqs            Attempt to install host prerequisites on Debian/Ubuntu (requires root)
  --without-local-ldap         Skip local LDAP baseline
  --with-live-office           Install live DocSpace + Workspace after base install
  --office-host <dns-or-ip>    Public host/IP for the live office cutover
  --office-auto-host           Auto-detect the primary IPv4 for live office cutover
  --docspace-port <port>       Internal DocSpace port for same-host live mode
  --workspace-port <port>      Internal Workspace port for same-host live mode
  --workspace-with-community   Keep Calendar and expose Community
  --workspace-calendar-only    Keep only Calendar in Workspace Wave 1
  --skip-office-hardware-check Skip host hardware guard for live office
  --simple-passwords           Use admin2026 / test2026 for the bootstrap users
  --regenerate-env             Overwrite existing .env with a freshly generated baseline
  --verify-only                Validate bootstrap prerequisites without changing the system
  -h, --help                   Show help
EOF
}

fail() {
  echo "[install-from-git] ERROR: $*" >&2
  exit 1
}

ensure_command() {
  local command_name="${1:-}"
  command -v "${command_name}" >/dev/null 2>&1 || fail "required command is missing: ${command_name}"
}

require_root_if_needed() {
  if [ "${INSTALL_PREREQS}" = "1" ] || [ "${WITH_LIVE_OFFICE}" = "1" ]; then
    [ "$(id -u)" -eq 0 ] || fail "this mode requires root; run with sudo"
  fi
}

prepare_env() {
  local env_file="${ROOT_DIR}/.env"

  if [ -f "${env_file}" ] && [ "${REGENERATE_ENV}" != "1" ]; then
    echo "[install-from-git] using existing .env"
  else
    if [ -f "${env_file}" ]; then
      cp "${env_file}" "${env_file}.before-git-bootstrap.$(date +%Y%m%d-%H%M%S)"
    fi

    rm -f "${env_file}"

    DOCFLOW_PROJECT_ROOT="${ROOT_DIR}" \
    DOCFLOW_DOMAIN="docflow.hospital.local" \
    DOCFLOW_OFFICE_DEPLOYMENT_MODE="shell_only" \
    bash "${ROOT_DIR}/ops/generate_prod_env.sh" "${env_file}"
  fi

  if [ "${GENERATE_SIMPLE_PASSWORDS}" = "1" ]; then
    docflow_set_env_value "${env_file}" "DOCFLOW_ADMIN_PASSWORD" "admin2026"
    docflow_set_env_value "${env_file}" "DOCFLOW_ROLE_DEFAULT_PASSWORD" "test2026"
    docflow_set_env_value "${env_file}" "DOCFLOW_MANAGER_USERNAME" "head"
    docflow_set_env_value "${env_file}" "DOCFLOW_EMPLOYEE_USERNAME" "doctor"
    docflow_set_env_value "${env_file}" "DOCFLOW_REQUESTER_USERNAME" "registry"
    docflow_set_env_value "${env_file}" "DOCFLOW_OFFICE_USERNAME" "office"
    docflow_set_env_value "${env_file}" "DOCFLOW_NURSE_USERNAME" "nurse"
  fi
}

write_install_summary() {
  mkdir -p "${ROOT_DIR}/runtime/monitoring"
  cat > "${ROOT_DIR}/runtime/monitoring/install_from_git_summary.txt" <<EOF
installed_at=$(date -Iseconds)
root_dir=${ROOT_DIR}
with_local_ldap=${WITH_LOCAL_LDAP}
with_live_office=${WITH_LIVE_OFFICE}
workspace_scope=${WORKSPACE_SCOPE}
simple_passwords=${GENERATE_SIMPLE_PASSWORDS}
regenerate_env=${REGENERATE_ENV}
EOF
}

create_bootstrap_seed_dir() {
  local seed_dir
  seed_dir="$(mktemp -d)"
  mkdir -p "${seed_dir}/mariadb" "${seed_dir}/bridge" "${seed_dir}/naudoc" "${seed_dir}/uploads"

  cp "${ROOT_DIR}/ops/bootstrap-seed/mariadb/rukovoditel.sql" "${seed_dir}/mariadb/rukovoditel.sql"
  cp "${ROOT_DIR}/ops/bootstrap-seed/bridge/bridge.db" "${seed_dir}/bridge/bridge.db"
  cp "${ROOT_DIR}/naudoc_project/var/Data.fs" "${seed_dir}/naudoc/Data.fs"
  cp "${ROOT_DIR}/ops/bootstrap-seed/uploads/rukovoditel_uploads.tar.gz" "${seed_dir}/uploads/rukovoditel_uploads.tar.gz"

  cat > "${seed_dir}/manifest.txt" <<EOF
source=ops/bootstrap-seed + repo tracked Data.fs
created_at=$(date -Iseconds)
EOF

  printf '%s\n' "${seed_dir}"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --install-prereqs)
      INSTALL_PREREQS=1
      shift
      ;;
    --without-local-ldap)
      WITH_LOCAL_LDAP=0
      shift
      ;;
    --with-live-office)
      WITH_LIVE_OFFICE=1
      shift
      ;;
    --office-host)
      OFFICE_HOST="${2:-}"
      shift 2
      ;;
    --office-auto-host)
      OFFICE_AUTO_HOST=1
      shift
      ;;
    --docspace-port)
      DOCSPACE_PORT="${2:-}"
      shift 2
      ;;
    --workspace-port)
      WORKSPACE_PORT="${2:-}"
      shift 2
      ;;
    --workspace-with-community)
      WORKSPACE_SCOPE="with_community"
      shift
      ;;
    --workspace-calendar-only)
      WORKSPACE_SCOPE="calendar_only"
      shift
      ;;
    --skip-office-hardware-check)
      SKIP_OFFICE_HARDWARE_CHECK=1
      shift
      ;;
    --simple-passwords)
      GENERATE_SIMPLE_PASSWORDS=1
      shift
      ;;
    --regenerate-env)
      REGENERATE_ENV=1
      shift
      ;;
    --verify-only)
      VERIFY_ONLY=1
      shift
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

require_root_if_needed

if [ ! -d "${ROOT_DIR}/.git" ]; then
  fail "run this installer from the project git checkout"
fi

if [ ! -f "${ROOT_DIR}/ops/bootstrap-seed/mariadb/rukovoditel.sql" ] || \
   [ ! -f "${ROOT_DIR}/ops/bootstrap-seed/bridge/bridge.db" ] || \
   [ ! -f "${ROOT_DIR}/ops/bootstrap-seed/uploads/rukovoditel_uploads.tar.gz" ]; then
  fail "bootstrap seed is missing in ops/bootstrap-seed"
fi

if [ "${INSTALL_PREREQS}" = "1" ]; then
  bash "${ROOT_DIR}/ops/install_server_prereqs.sh"
fi

ensure_command docker
docker compose version >/dev/null 2>&1 || fail "docker compose is required"
ensure_command bash
ensure_command tar

if [ "${VERIFY_ONLY}" = "1" ]; then
  tmp_seed_dir="$(create_bootstrap_seed_dir)"
  trap 'rm -rf "${tmp_seed_dir}"' EXIT
  bash "${ROOT_DIR}/ops/restore_all.sh" "${tmp_seed_dir}" --verify-only
  echo "[install-from-git] verify-only: git bootstrap prerequisites are ready"
  exit 0
fi

prepare_env

echo "[install-from-git] start base stack"
bash "${ROOT_DIR}/ops/start_stack.sh"

BOOTSTRAP_SEED_DIR="$(create_bootstrap_seed_dir)"
trap 'rm -rf "${BOOTSTRAP_SEED_DIR}"' EXIT

echo "[install-from-git] restore bootstrap seed"
bash "${ROOT_DIR}/ops/restore_all.sh" "${BOOTSTRAP_SEED_DIR}"

if [ "${WITH_LOCAL_LDAP}" = "1" ]; then
  echo "[install-from-git] re-bootstrap local ldap"
  bash "${ROOT_DIR}/ops/bootstrap_local_ldap.sh"
fi

echo "[install-from-git] reprovision users"
bash "${ROOT_DIR}/rukovoditel-test/provision_test_users.sh"

echo "[install-from-git] prepare baseline"
bash "${ROOT_DIR}/rukovoditel-test/prepare_hospital_baseline.sh"

echo "[install-from-git] export LAN packet"
bash "${ROOT_DIR}/ops/export_lan_manual_test_packet.sh"

echo "[install-from-git] write install summary"
write_install_summary

echo "[install-from-git] export quick start"
bash "${ROOT_DIR}/ops/export_server_quickstart.sh"

if [ "${WITH_LIVE_OFFICE}" = "1" ]; then
  LIVE_OFFICE_ARGS=()

  if [ -n "${OFFICE_HOST}" ]; then
    LIVE_OFFICE_ARGS+=(--host "${OFFICE_HOST}")
  elif [ "${OFFICE_AUTO_HOST}" = "1" ]; then
    LIVE_OFFICE_ARGS+=(--auto-host)
  fi

  if [ -n "${DOCSPACE_PORT}" ]; then
    LIVE_OFFICE_ARGS+=(--docspace-port "${DOCSPACE_PORT}")
  fi

  if [ -n "${WORKSPACE_PORT}" ]; then
    LIVE_OFFICE_ARGS+=(--workspace-port "${WORKSPACE_PORT}")
  fi

  if [ "${WORKSPACE_SCOPE}" = "with_community" ]; then
    LIVE_OFFICE_ARGS+=(--workspace-with-community)
  else
    LIVE_OFFICE_ARGS+=(--workspace-calendar-only)
  fi

  if [ "${SKIP_OFFICE_HARDWARE_CHECK}" = "1" ]; then
    LIVE_OFFICE_ARGS+=(--skip-hardware-check)
  fi

  echo "[install-from-git] install live office layer"
  bash "${ROOT_DIR}/ops/install_office_live_same_host.sh" "${LIVE_OFFICE_ARGS[@]}"
fi

echo "[install-from-git] final checks"
bash "${ROOT_DIR}/ops/check_stack.sh"
bash "${ROOT_DIR}/ops/smoke_test_stack.sh"
python3 "${ROOT_DIR}/ops/prod_readiness_audit.py" | tee "${ROOT_DIR}/runtime/monitoring/git_install_prod_readiness.json"
python3 "${ROOT_DIR}/ops/monitoring_snapshot.py" | tee "${ROOT_DIR}/runtime/monitoring/git_install_monitoring_snapshot.json"
python3 "${ROOT_DIR}/ops/audit_ecosystem_integration.py" | tee "${ROOT_DIR}/runtime/monitoring/git_install_ecosystem_audit.json"
python3 "${ROOT_DIR}/ops/audit_onlyoffice_integration.py" | tee "${ROOT_DIR}/runtime/monitoring/git_install_onlyoffice_audit.json"
if [ "${WITH_LIVE_OFFICE}" = "1" ] && command -v node >/dev/null 2>&1; then
  node "${ROOT_DIR}/ops/audit_live_office_auth.mjs" | tee "${ROOT_DIR}/runtime/monitoring/git_install_live_office_auth.json"
fi

cat > "${ROOT_DIR}/runtime/monitoring/git_install_summary.txt" <<EOF
installed_at=$(date -Iseconds)
root_dir=${ROOT_DIR}
with_local_ldap=${WITH_LOCAL_LDAP}
with_live_office=${WITH_LIVE_OFFICE}
simple_passwords=${GENERATE_SIMPLE_PASSWORDS}
access_points=${ROOT_DIR}/runtime/monitoring/access_points.txt
lan_manual_packet=${ROOT_DIR}/.tmp_lan_manual_test/LAN_MANUAL_TEST_PACKET.md
quick_start=${ROOT_DIR}/runtime/monitoring/START_HERE.txt
EOF

echo "[install-from-git] done"
echo "[install-from-git] platform: $(grep '^RUKOVODITEL_PUBLIC_URL=' "${ROOT_DIR}/.env" | cut -d= -f2-)"
echo "[install-from-git] access packet: ${ROOT_DIR}/.tmp_lan_manual_test/LAN_MANUAL_TEST_PACKET.md"
echo "[install-from-git] quick start: ${ROOT_DIR}/runtime/monitoring/START_HERE.txt"
cat "${ROOT_DIR}/runtime/monitoring/START_HERE.txt"
