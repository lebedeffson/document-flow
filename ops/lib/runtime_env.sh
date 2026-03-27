#!/usr/bin/env bash

docflow_default_root() {
  local caller_dir="${1:-$(pwd)}"
  (cd "${caller_dir}/.." && pwd)
}

docflow_trim_trailing_slash() {
  local value="${1:-}"
  value="${value%/}"
  printf '%s\n' "${value}"
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

docflow_office_public_base() {
  printf '%s/office\n' "$(docflow_public_base)"
}

docflow_http_base() {
  docflow_build_url "http" "$(docflow_public_host)" "$(docflow_gateway_http_port)"
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

docflow_export_runtime() {
  export DOCFLOW_PUBLIC_HOST
  DOCFLOW_PUBLIC_HOST="$(docflow_public_host)"

  export DOCFLOW_PUBLIC_BASE
  DOCFLOW_PUBLIC_BASE="$(docflow_public_base)"

  export DOCFLOW_DOCS_BASE
  DOCFLOW_DOCS_BASE="$(docflow_docs_base)"

  export DOCFLOW_BRIDGE_PUBLIC_BASE
  DOCFLOW_BRIDGE_PUBLIC_BASE="$(docflow_bridge_public_base)"

  export DOCFLOW_OFFICE_PUBLIC_BASE
  DOCFLOW_OFFICE_PUBLIC_BASE="$(docflow_office_public_base)"

  export DOCFLOW_HTTP_BASE
  DOCFLOW_HTTP_BASE="$(docflow_http_base)"

  export GATEWAY_CONTAINER_NAME="${GATEWAY_CONTAINER_NAME:-naudoc_gateway_test}"
  export MIDDLEWARE_COMPOSE_PROJECT_NAME="${MIDDLEWARE_COMPOSE_PROJECT_NAME:-middleware}"
  export RUKOVODITEL_COMPOSE_PROJECT_NAME="${RUKOVODITEL_COMPOSE_PROJECT_NAME:-rukovoditel-test}"
  export BRIDGE_CONTAINER="${BRIDGE_CONTAINER:-naudoc_bridge_test}"
  export RUKOVODITEL_CONTAINER_NAME="${RUKOVODITEL_CONTAINER_NAME:-rukovoditel_test}"
  export RUKOVODITEL_DB_CONTAINER="${RUKOVODITEL_DB_CONTAINER:-rukovoditel_db_test}"
  export ONLYOFFICE_CONTAINER_NAME="${ONLYOFFICE_CONTAINER_NAME:-onlyoffice_docs_test}"
  export RUKOVODITEL_SYNC_WORKER_CONTAINER_NAME="${RUKOVODITEL_SYNC_WORKER_CONTAINER_NAME:-rukovoditel_sync_worker_test}"
  export NAUDOC_LEGACY_CONTAINER="${NAUDOC_LEGACY_CONTAINER:-naudoc34_legacy}"
  export NAUDOC_USERNAME="${NAUDOC_USERNAME:-admin}"
  export NAUDOC_PASSWORD="${NAUDOC_PASSWORD:-admin}"
  export RUKOVODITEL_DB_NAME="${RUKOVODITEL_DB_NAME:-rukovoditel}"
  export RUKOVODITEL_DB_USER="${RUKOVODITEL_DB_USER:-rukovoditel}"
  export RUKOVODITEL_DB_PASSWORD="${RUKOVODITEL_DB_PASSWORD:-rukovoditel}"
  export RUKOVODITEL_DB_ROOT_PASSWORD="${RUKOVODITEL_DB_ROOT_PASSWORD:-root_rukovoditel}"
  export ONLYOFFICE_JWT_SECRET="${ONLYOFFICE_JWT_SECRET:-onlyoffice_dev_secret}"
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
