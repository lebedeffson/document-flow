#!/usr/bin/env bash

docflow_default_root() {
  local caller_dir="${1:-$(pwd)}"
  (cd "${caller_dir}/.." && pwd)
}

docflow_is_msys_shell() {
  case "${OSTYPE:-}" in
    msys*|cygwin*)
      return 0
      ;;
  esac

  return 1
}

if docflow_is_msys_shell && command -v python >/dev/null 2>&1; then
  python3() {
    command python "$@"
  }
fi

docflow_enable_msys_docker_compat() {
  if docflow_is_msys_shell; then
    export MSYS_NO_PATHCONV=1
    export MSYS2_ARG_CONV_EXCL="*"
  fi
}

docflow_host_path_for_docker() {
  local path="${1:-}"

  if [ -z "${path}" ]; then
    printf '\n'
    return 0
  fi

  if docflow_is_msys_shell && command -v cygpath >/dev/null 2>&1; then
    cygpath -w "${path}"
    return 0
  fi

  printf '%s\n' "${path}"
}

docflow_docker_exec() {
  if docflow_is_msys_shell; then
    MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*" docker exec "$@"
    return $?
  fi

  docker exec "$@"
}

docflow_docker_cp_to_container() {
  local host_path="${1:-}"
  local container_path="${2:-}"
  local docker_host_path="${host_path}"

  if [ -z "${host_path}" ] || [ -z "${container_path}" ]; then
    echo "[docker] usage: docflow_docker_cp_to_container <host-path> <container:path>" >&2
    return 1
  fi

  if docflow_is_msys_shell; then
    docker_host_path="$(docflow_host_path_for_docker "${host_path}")"
    MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*" docker cp "${docker_host_path}" "${container_path}"
    return $?
  fi

  docker cp "${docker_host_path}" "${container_path}"
}

docflow_docker_cp_from_container() {
  local container_path="${1:-}"
  local host_path="${2:-}"
  local docker_host_path="${host_path}"

  if [ -z "${container_path}" ] || [ -z "${host_path}" ]; then
    echo "[docker] usage: docflow_docker_cp_from_container <container:path> <host-path>" >&2
    return 1
  fi

  if docflow_is_msys_shell; then
    docker_host_path="$(docflow_host_path_for_docker "${host_path}")"
    MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*" docker cp "${container_path}" "${docker_host_path}"
    return $?
  fi

  docker cp "${container_path}" "${docker_host_path}"
}

docflow_trim_trailing_slash() {
  local value="${1:-}"
  value="${value%/}"
  printf '%s\n' "${value}"
}

docflow_is_ipv4_literal() {
  local value="${1:-}"
  [[ "${value}" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]
}

docflow_is_internal_gateway_target_host() {
  local value="${1:-}"
  [[ "${value}" == "host.docker.internal" || "${value}" == "localhost" || "${value}" == 127.* ]]
}

docflow_list_non_loopback_ipv4s() {
  if command -v ip >/dev/null 2>&1; then
    ip -4 -o addr show scope global up 2>/dev/null | awk '$2 !~ /^(docker|br-|veth|virbr|lo)/ {print $4}' | cut -d/ -f1 | awk '!seen[$0]++'
    return 0
  fi

  if command -v hostname >/dev/null 2>&1; then
    hostname -I 2>/dev/null | tr ' ' '\n' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' | grep -v '^127\.' | awk '!seen[$0]++'
    return 0
  fi
}

docflow_detect_primary_ipv4() {
  local candidate=""
  local preferred_host="${DOCFLOW_ACCESS_HOST:-${GATEWAY_SERVER_NAME:-}}"

  if docflow_is_ipv4_literal "${preferred_host}"; then
    if docflow_list_non_loopback_ipv4s | grep -Fxq "${preferred_host}"; then
      printf '%s\n' "${preferred_host}"
      return 0
    fi
  fi

  if command -v ip >/dev/null 2>&1; then
    candidate="$(ip -4 route get 1.1.1.1 2>/dev/null | awk '/src / {for (i = 1; i <= NF; ++i) if ($i == "src") {print $(i+1); exit}}')"
  fi

  if [ -z "${candidate}" ]; then
    candidate="$(docflow_list_non_loopback_ipv4s | head -n 1)"
  fi

  if [ -n "${candidate}" ]; then
    printf '%s\n' "${candidate}"
    return 0
  fi

  return 1
}

docflow_build_url() {
  local scheme="${1:-https}"
  local host="${2:-localhost}"
  local port="${3:-}"
  local path="${4:-}"

  if [ -z "${port}" ]; then
    printf '%s://%s%s\n' "${scheme}" "${host}" "${path}"
    return 0
  fi

  if { [ "${scheme}" = "https" ] && [ "${port}" = "443" ]; } || { [ "${scheme}" = "http" ] && [ "${port}" = "80" ]; }; then
    printf '%s://%s%s\n' "${scheme}" "${host}" "${path}"
    return 0
  fi

  printf '%s://%s:%s%s\n' "${scheme}" "${host}" "${port}" "${path}"
}

docflow_public_host() {
  if [ -n "${DOCFLOW_ACCESS_HOST:-}" ]; then
    printf '%s\n' "${DOCFLOW_ACCESS_HOST}"
    return 0
  fi

  printf '%s\n' "${GATEWAY_SERVER_NAME:-localhost}"
}

docflow_gateway_http_port() {
  printf '%s\n' "${GATEWAY_BIND_HTTP_PORT:-18090}"
}

docflow_gateway_https_port() {
  printf '%s\n' "${GATEWAY_BIND_HTTPS_PORT:-18443}"
}

docflow_public_base() {
  if [ -n "${RUKOVODITEL_PUBLIC_URL:-}" ]; then
    docflow_trim_trailing_slash "${RUKOVODITEL_PUBLIC_URL}"
    return 0
  fi

  docflow_build_url "https" "$(docflow_public_host)" "$(docflow_gateway_https_port)"
}

docflow_docs_base() {
  if [ -n "${NAUDOC_PUBLIC_URL:-}" ]; then
    docflow_trim_trailing_slash "${NAUDOC_PUBLIC_URL}"
    return 0
  fi

  printf '%s/docs\n' "$(docflow_public_base)"
}

docflow_bridge_public_base() {
  printf '%s/bridge\n' "$(docflow_public_base)"
}

docflow_docspace_public_base() {
  if [ -n "${DOCSPACE_PUBLIC_URL:-}" ]; then
    docflow_trim_trailing_slash "${DOCSPACE_PUBLIC_URL}"
    return 0
  fi

  printf '%s/docspace\n' "$(docflow_public_base)"
}

docflow_workspace_public_base() {
  if [ -n "${WORKSPACE_PUBLIC_URL:-}" ]; then
    docflow_trim_trailing_slash "${WORKSPACE_PUBLIC_URL}"
    return 0
  fi

  printf '%s/workspace\n' "$(docflow_public_base)"
}

docflow_office_public_base() {
  printf '%s/office\n' "$(docflow_public_base)"
}

docflow_http_base() {
  docflow_build_url "http" "$(docflow_public_host)" "$(docflow_gateway_http_port)"
}

docflow_local_probe_ip() {
  printf '%s\n' "${DOCFLOW_LOCAL_PROBE_IP:-127.0.0.1}"
}

docflow_url_field() {
  local url="${1:-}"
  local field="${2:-}"

  python3 - "${url}" "${field}" <<'PY'
from urllib.parse import urlparse
import sys

url = sys.argv[1]
field = sys.argv[2]
parsed = urlparse(url)

default_port = 443 if parsed.scheme == "https" else 80
values = {
    "scheme": parsed.scheme,
    "host": parsed.hostname or "",
    "port": str(parsed.port or default_port),
    "path": (parsed.path or "/") + (f"?{parsed.query}" if parsed.query else ""),
}
print(values.get(field, ""), end="")
PY
}

docflow_env_file_path() {
  local root_dir="${1:-}"
  if [ -n "${DOCFLOW_ENV_FILE:-}" ]; then
    printf '%s\n' "${DOCFLOW_ENV_FILE}"
    return 0
  fi

  printf '%s/.env\n' "${root_dir}"
}

docflow_load_env() {
  local root_dir="${1:-}"
  if [ -z "${root_dir}" ]; then
    return 0
  fi

  local env_file
  env_file="$(docflow_env_file_path "${root_dir}")"
  if [ -f "${env_file}" ]; then
    set -a
    # shellcheck disable=SC1090
    . "${env_file}"
    set +a
  fi
}

docflow_set_env_value() {
  local env_file="${1:-}"
  local key="${2:-}"
  local value="${3:-}"

  if [ -z "${env_file}" ] || [ -z "${key}" ]; then
    echo "[env] usage: docflow_set_env_value <env-file> <key> <value>" >&2
    return 1
  fi

  python3 - "${env_file}" "${key}" "${value}" <<'PY'
from pathlib import Path
import sys

env_path = Path(sys.argv[1])
key = sys.argv[2]
value = sys.argv[3]

lines = []
found = False

if env_path.exists():
    lines = env_path.read_text(encoding="utf-8").splitlines()

updated = []
for line in lines:
    stripped = line.strip()
    if stripped.startswith(f"{key}="):
        updated.append(f"{key}={value}")
        found = True
    else:
        updated.append(line)

if not found:
    if updated and updated[-1].strip():
        updated.append("")
    updated.append(f"{key}={value}")

content = "\n".join(updated).rstrip("\n") + "\n"
env_path.write_text(content, encoding="utf-8")
PY
}

docflow_is_absolute_path() {
  local value="${1:-}"
  [[ "${value}" = /* ]]
}

docflow_resolve_path() {
  local root_dir="${1:-${PROJECT_ROOT:-${PWD}}}"
  local value="${2:-}"

  if [ -z "${value}" ]; then
    printf '\n'
    return 0
  fi

  if docflow_is_absolute_path "${value}"; then
    printf '%s\n' "${value}"
    return 0
  fi

  printf '%s\n' "${root_dir%/}/${value#./}"
}

docflow_find_mount_target() {
  local path="${1:-}"

  if [ -z "${path}" ]; then
    return 1
  fi

  if command -v findmnt >/dev/null 2>&1; then
    findmnt -T "${path}" -n -o TARGET 2>/dev/null
    return $?
  fi

  return 1
}

docflow_find_mount_source() {
  local path="${1:-}"

  if [ -z "${path}" ]; then
    return 1
  fi

  if command -v findmnt >/dev/null 2>&1; then
    findmnt -T "${path}" -n -o SOURCE 2>/dev/null
    return $?
  fi

  return 1
}

docflow_assert_data_root_is_mounted() {
  local data_root="${1:-}"
  local reference_path="${2:-${PROJECT_ROOT:-${PWD}}}"

  if [ -z "${data_root}" ]; then
    echo "[env] data root path is empty" >&2
    return 1
  fi

  if ! docflow_is_absolute_path "${data_root}"; then
    echo "[env] data root must be an absolute path: ${data_root}" >&2
    return 1
  fi

  if [ ! -d "${data_root}" ]; then
    if ! mkdir -p "${data_root}"; then
      echo "[env] cannot create data root path: ${data_root}" >&2
      return 1
    fi
  fi

  local mount_target=""
  mount_target="$(docflow_find_mount_target "${data_root}" || true)"
  local mount_source=""
  mount_source="$(docflow_find_mount_source "${data_root}" || true)"

  if [ -z "${mount_target}" ]; then
    echo "[env] could not verify mountpoint for ${data_root}; install findmnt/util-linux or omit --data-root" >&2
    return 1
  fi

  if [ "${mount_target}" = "/" ]; then
    echo "[env] ${data_root} resolves to the system filesystem (/); mount the separate disk first or omit --data-root" >&2
    return 1
  fi

  if [ -n "${reference_path}" ]; then
    local reference_source=""
    reference_source="$(docflow_find_mount_source "${reference_path}" || true)"
    if [ -n "${reference_source}" ] && [ -n "${mount_source}" ] && [ "${reference_source}" = "${mount_source}" ]; then
      echo "[env] ${data_root} is on the same filesystem as ${reference_path}; mount the separate disk first or omit --data-root" >&2
      return 1
    fi
  fi
}

docflow_configure_data_root_env() {
  local env_file="${1:-}"
  local data_root="${2:-}"

  if [ -z "${env_file}" ] || [ -z "${data_root}" ]; then
    echo "[env] usage: docflow_configure_data_root_env <env-file> <data-root>" >&2
    return 1
  fi

  docflow_assert_data_root_is_mounted "${data_root}" "$(dirname "${env_file}")" || return 1

  mkdir -p \
    "${data_root}/mariadb" \
    "${data_root}/bridge" \
    "${data_root}/naudoc-var" \
    "${data_root}/onlyoffice-data" \
    "${data_root}/onlyoffice-logs" \
    "${data_root}/onlyoffice-lib" \
    "${data_root}/onlyoffice-db" \
    "${data_root}/ldap-data" \
    "${data_root}/ldap-config" \
    "${data_root}/gateway-certs"

  docflow_set_env_value "${env_file}" "DOCFLOW_DATA_ROOT" "${data_root}"
  docflow_set_env_value "${env_file}" "RUKOVODITEL_DB_DATA_MOUNT" "${data_root}/mariadb"
  docflow_set_env_value "${env_file}" "BRIDGE_DATA_MOUNT" "${data_root}/bridge"
  docflow_set_env_value "${env_file}" "NAUDOC_VAR_MOUNT" "${data_root}/naudoc-var"
  docflow_set_env_value "${env_file}" "ONLYOFFICE_DATA_MOUNT" "${data_root}/onlyoffice-data"
  docflow_set_env_value "${env_file}" "ONLYOFFICE_LOGS_MOUNT" "${data_root}/onlyoffice-logs"
  docflow_set_env_value "${env_file}" "ONLYOFFICE_LIB_MOUNT" "${data_root}/onlyoffice-lib"
  docflow_set_env_value "${env_file}" "ONLYOFFICE_DB_MOUNT" "${data_root}/onlyoffice-db"
  docflow_set_env_value "${env_file}" "LDAP_DATA_MOUNT" "${data_root}/ldap-data"
  docflow_set_env_value "${env_file}" "LDAP_CONFIG_MOUNT" "${data_root}/ldap-config"
  docflow_set_env_value "${env_file}" "GATEWAY_CERTS_MOUNT" "${data_root}/gateway-certs"
}

docflow_prepare_host_storage() {
  local data_root="${DOCFLOW_DATA_ROOT:-}"
  local reference_path="${PROJECT_ROOT:-${PWD}}"

  if [ -n "${data_root}" ]; then
    docflow_assert_data_root_is_mounted "${data_root}" "${reference_path}" || return 1
  fi

  local mount_path=""
  for mount_path in \
    "${RUKOVODITEL_DB_DATA_MOUNT:-}" \
    "${BRIDGE_DATA_MOUNT:-}" \
    "${NAUDOC_VAR_MOUNT:-}" \
    "${ONLYOFFICE_DATA_MOUNT:-}" \
    "${ONLYOFFICE_LOGS_MOUNT:-}" \
    "${ONLYOFFICE_LIB_MOUNT:-}" \
    "${ONLYOFFICE_DB_MOUNT:-}" \
    "${LDAP_DATA_MOUNT:-}" \
    "${LDAP_CONFIG_MOUNT:-}" \
    "${GATEWAY_CERTS_MOUNT:-}"; do
    if docflow_is_absolute_path "${mount_path}"; then
      mkdir -p "${mount_path}"
    fi
  done

  local office_live_root=""
  office_live_root="$(docflow_office_live_root "${reference_path}")"
  if [ -n "${office_live_root}" ] && docflow_is_absolute_path "${office_live_root}"; then
    mkdir -p \
      "${office_live_root}" \
      "$(docflow_docspace_volumes_dir "${reference_path}")" \
      "$(docflow_workspace_base_dir "${reference_path}")"
  fi
}

docflow_office_live_root() {
  local root_dir="${1:-${PROJECT_ROOT:-${PWD}}}"

  if [ -z "${DOCFLOW_DATA_ROOT:-}" ] || ! docflow_is_absolute_path "${DOCFLOW_DATA_ROOT}"; then
    printf '\n'
    return 0
  fi

  printf '%s/office-live\n' "${DOCFLOW_DATA_ROOT}"
}

docflow_docspace_volumes_dir() {
  local root_dir="${1:-${PROJECT_ROOT:-${PWD}}}"
  local office_live_root=""
  office_live_root="$(docflow_office_live_root "${root_dir}")"

  if [ -z "${office_live_root}" ]; then
    printf '\n'
    return 0
  fi

  printf '%s/docspace-volumes\n' "${office_live_root}"
}

docflow_workspace_base_dir() {
  local root_dir="${1:-${PROJECT_ROOT:-${PWD}}}"
  local office_live_root=""
  office_live_root="$(docflow_office_live_root "${root_dir}")"

  if [ -z "${office_live_root}" ]; then
    printf '\n'
    return 0
  fi

  printf '%s/workspace\n' "${office_live_root}"
}

docflow_naudoc_var_path() {
  local root_dir="${1:-${PROJECT_ROOT:-${PWD}}}"
  docflow_resolve_path "${root_dir}" "${NAUDOC_VAR_MOUNT:-./naudoc_project/var}"
}

docflow_naudoc_data_file() {
  local root_dir="${1:-${PROJECT_ROOT:-${PWD}}}"
  printf '%s/Data.fs\n' "$(docflow_naudoc_var_path "${root_dir}")"
}

docflow_export_runtime() {
  export DOCFLOW_PUBLIC_HOST
  DOCFLOW_PUBLIC_HOST="$(docflow_public_host)"

  export DOCFLOW_PUBLIC_BASE
  DOCFLOW_PUBLIC_BASE="$(docflow_public_base)"

  export DOCFLOW_DOCS_BASE
  DOCFLOW_DOCS_BASE="$(docflow_docs_base)"

  export DOCFLOW_BRIDGE_PUBLIC_BASE
  DOCFLOW_BRIDGE_PUBLIC_BASE="$(docflow_bridge_public_base)"

  export DOCFLOW_DOCSPACE_PUBLIC_BASE
  DOCFLOW_DOCSPACE_PUBLIC_BASE="$(docflow_docspace_public_base)"

  export DOCFLOW_WORKSPACE_PUBLIC_BASE
  DOCFLOW_WORKSPACE_PUBLIC_BASE="$(docflow_workspace_public_base)"

  export DOCFLOW_OFFICE_PUBLIC_BASE
  DOCFLOW_OFFICE_PUBLIC_BASE="$(docflow_office_public_base)"

  export DOCFLOW_HTTP_BASE
  DOCFLOW_HTTP_BASE="$(docflow_http_base)"

  export GATEWAY_CONTAINER_NAME="${GATEWAY_CONTAINER_NAME:-naudoc_gateway_test}"
  export GATEWAY_COMPOSE_PROJECT_NAME="${GATEWAY_COMPOSE_PROJECT_NAME:-docflow_gateway}"
  export MIDDLEWARE_COMPOSE_PROJECT_NAME="${MIDDLEWARE_COMPOSE_PROJECT_NAME:-middleware}"
  export RUKOVODITEL_COMPOSE_PROJECT_NAME="${RUKOVODITEL_COMPOSE_PROJECT_NAME:-rukovoditel-test}"
  export BRIDGE_CONTAINER="${BRIDGE_CONTAINER:-naudoc_bridge_test}"
  export RUKOVODITEL_CONTAINER_NAME="${RUKOVODITEL_CONTAINER_NAME:-rukovoditel_test}"
  export RUKOVODITEL_DB_CONTAINER="${RUKOVODITEL_DB_CONTAINER:-rukovoditel_db_test}"
  export ONLYOFFICE_CONTAINER_NAME="${ONLYOFFICE_CONTAINER_NAME:-onlyoffice_docs_test}"
  export RUKOVODITEL_SYNC_WORKER_CONTAINER_NAME="${RUKOVODITEL_SYNC_WORKER_CONTAINER_NAME:-rukovoditel_sync_worker_test}"
  export NAUDOC_LEGACY_CONTAINER="${NAUDOC_LEGACY_CONTAINER:-naudoc34_legacy}"
  export NAUDOC_LEGACY_COMPOSE_PROJECT="${NAUDOC_LEGACY_COMPOSE_PROJECT:-docflow_legacy}"
  export NAUDOC_USERNAME="${NAUDOC_USERNAME:-admin}"
  export NAUDOC_PASSWORD="${NAUDOC_PASSWORD:-admin}"
  export RUKOVODITEL_DB_NAME="${RUKOVODITEL_DB_NAME:-rukovoditel}"
  export RUKOVODITEL_DB_USER="${RUKOVODITEL_DB_USER:-rukovoditel}"
  export RUKOVODITEL_DB_PASSWORD="${RUKOVODITEL_DB_PASSWORD:-rukovoditel}"
  export RUKOVODITEL_DB_ROOT_PASSWORD="${RUKOVODITEL_DB_ROOT_PASSWORD:-root_rukovoditel}"
  export ONLYOFFICE_JWT_SECRET="${ONLYOFFICE_JWT_SECRET:-onlyoffice_dev_secret}"
  export LDAP_DOMAIN="${LDAP_DOMAIN:-hospital.local}"
  export LDAP_ORGANISATION="${LDAP_ORGANISATION:-Hospital_DocFlow}"
  export LDAP_ADMIN_PASSWORD="${LDAP_ADMIN_PASSWORD:-ldap_admin_dev}"
  export LDAP_CONFIG_PASSWORD="${LDAP_CONFIG_PASSWORD:-ldap_config_dev}"
  export LDAP_BIND_PASSWORD="${LDAP_BIND_PASSWORD:-ldap_bind_dev}"
  export DOCFLOW_SHOW_DEMO_LOGIN_MODES="${DOCFLOW_SHOW_DEMO_LOGIN_MODES:-0}"
  export DOCFLOW_ADMIN_USERNAME="${DOCFLOW_ADMIN_USERNAME:-admin}"
  export DOCFLOW_ADMIN_PASSWORD="${DOCFLOW_ADMIN_PASSWORD:-admin123}"
  export DOCFLOW_ROLE_DEFAULT_PASSWORD="${DOCFLOW_ROLE_DEFAULT_PASSWORD:-rolepass123}"
  export DOCFLOW_MANAGER_USERNAME="${DOCFLOW_MANAGER_USERNAME:-department.head}"
  export DOCFLOW_EMPLOYEE_USERNAME="${DOCFLOW_EMPLOYEE_USERNAME:-clinician.primary}"
  export DOCFLOW_REQUESTER_USERNAME="${DOCFLOW_REQUESTER_USERNAME:-registry.operator}"
  export DOCFLOW_OFFICE_USERNAME="${DOCFLOW_OFFICE_USERNAME:-records.office}"
  export DOCFLOW_NURSE_USERNAME="${DOCFLOW_NURSE_USERNAME:-nurse.coordinator}"
  export SYNC_INTERVAL_SECONDS="${SYNC_INTERVAL_SECONDS:-180}"
  export BRIDGE_REQUEST_TIMEOUT="${BRIDGE_REQUEST_TIMEOUT:-8}"
  export BRIDGE_GUNICORN_WORKERS="${BRIDGE_GUNICORN_WORKERS:-1}"
  export BRIDGE_GUNICORN_THREADS="${BRIDGE_GUNICORN_THREADS:-2}"
  export BRIDGE_GUNICORN_TIMEOUT="${BRIDGE_GUNICORN_TIMEOUT:-60}"
  export LDAP_CONTAINER_NAME="${LDAP_CONTAINER_NAME:-docflow_hospital_ldap}"
  export GATEWAY_IMAGE="${GATEWAY_IMAGE:-docflow/gateway:local}"
  export BRIDGE_IMAGE="${BRIDGE_IMAGE:-docflow/bridge:local}"
  export RUKOVODITEL_APP_IMAGE="${RUKOVODITEL_APP_IMAGE:-docflow/rukovoditel-app:local}"
  export NAUDOC_LEGACY_IMAGE="${NAUDOC_LEGACY_IMAGE:-docflow/naudoc-legacy:local}"
  export MARIADB_IMAGE="${MARIADB_IMAGE:-mariadb:10.11}"
  export ONLYOFFICE_IMAGE="${ONLYOFFICE_IMAGE:-onlyoffice/documentserver:latest}"
  export LDAP_IMAGE="${LDAP_IMAGE:-osixia/openldap:1.5.0}"
}

docflow_random_secret() {
  local length="${1:-32}"

  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex "${length}" 2>/dev/null | tr -d '\n'
    return 0
  fi

  python3 - "${length}" <<'PY'
import secrets
import sys
length = int(sys.argv[1])
print(secrets.token_hex(length), end="")
PY
}

docflow_verify_backup_dir() {
  local backup_dir="${1:-}"
  if [ -z "${backup_dir}" ] || [ ! -d "${backup_dir}" ]; then
    echo "[verify-backup] missing backup dir: ${backup_dir}" >&2
    return 1
  fi

  local manifest="${backup_dir}/manifest.txt"
  local checksums="${backup_dir}/SHA256SUMS"

  if [ ! -f "${manifest}" ]; then
    echo "[verify-backup] missing manifest: ${manifest}" >&2
    return 1
  fi

  if [ -f "${checksums}" ] && command -v sha256sum >/dev/null 2>&1; then
    (
      cd "${backup_dir}"
      sha256sum -c SHA256SUMS
    )
  fi
}
