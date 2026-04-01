#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ENV_FILE="$(docflow_env_file_path "${ROOT_DIR}")"
ACCESS_HOST_ARG=""
AUTO_OVERRIDE=""

usage() {
  cat <<'EOF'
Usage: bash ops/configure_access_host.sh [--host <dns-or-ip>] [--auto] [--env-file <path>]

Updates the current env file so one host value drives all public URLs:
- GATEWAY_SERVER_NAME
- GATEWAY_TLS_CN
- RUKOVODITEL_PUBLIC_URL
- NAUDOC_PUBLIC_URL
- DOCSPACE_PUBLIC_URL
- WORKSPACE_PUBLIC_URL
- ONLYOFFICE_PUBLIC_JS_API_URL
EOF
}

while [ "$#" -gt 0 ]; do
  case "${1}" in
    --host)
      ACCESS_HOST_ARG="${2:-}"
      shift 2
      ;;
    --host=*)
      ACCESS_HOST_ARG="${1#*=}"
      shift
      ;;
    --auto)
      AUTO_OVERRIDE="1"
      shift
      ;;
    --env-file)
      ENV_FILE="${2:-}"
      shift 2
      ;;
    --env-file=*)
      ENV_FILE="${1#*=}"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "[access-host] unknown argument: ${1}" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [ ! -f "${ENV_FILE}" ]; then
  echo "[access-host] missing env file: ${ENV_FILE}" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
. "${ENV_FILE}"
set +a

EXISTING_HOST="${DOCFLOW_ACCESS_HOST:-${GATEWAY_SERVER_NAME:-}}"
if [ -n "${AUTO_OVERRIDE}" ]; then
  AUTO_DETECT="${AUTO_OVERRIDE}"
elif [ -n "${DOCFLOW_ACCESS_HOST_AUTO:-}" ]; then
  AUTO_DETECT="${DOCFLOW_ACCESS_HOST_AUTO}"
elif [ -z "${EXISTING_HOST}" ] || [ "${EXISTING_HOST}" = "localhost" ]; then
  AUTO_DETECT="1"
else
  AUTO_DETECT="0"
fi

if [ -n "${ACCESS_HOST_ARG}" ] && [ -z "${AUTO_OVERRIDE}" ]; then
  AUTO_DETECT="0"
fi

ACCESS_HOST="${ACCESS_HOST_ARG:-${EXISTING_HOST}}"

if [ -z "${ACCESS_HOST_ARG}" ] && [ "${AUTO_DETECT}" = "1" ]; then
  ACCESS_HOST="$(docflow_detect_primary_ipv4 || true)"
fi

if [ -z "${ACCESS_HOST}" ]; then
  echo "[access-host] no access host configured" >&2
  echo "[access-host] set DOCFLOW_ACCESS_HOST in ${ENV_FILE} or run with --auto/--host" >&2
  exit 1
fi

HTTPS_PORT="${GATEWAY_EXTERNAL_HTTPS_PORT:-${GATEWAY_BIND_HTTPS_PORT:-443}}"
HTTP_PORT="${GATEWAY_BIND_HTTP_PORT:-80}"

HTTPS_SUFFIX=""
HTTPS_SUFFIX_ESCAPED=""
if [ "${HTTPS_PORT}" != "443" ]; then
  HTTPS_SUFFIX=":${HTTPS_PORT}"
  HTTPS_SUFFIX_ESCAPED="%3A${HTTPS_PORT}"
fi

HTTP_SUFFIX=""
if [ "${HTTP_PORT}" != "80" ]; then
  HTTP_SUFFIX=":${HTTP_PORT}"
fi

PUBLIC_BASE="$(docflow_build_url "https" "${ACCESS_HOST}" "${HTTPS_PORT}")"

docflow_set_env_value "${ENV_FILE}" "DOCFLOW_ACCESS_HOST" "${ACCESS_HOST}"
docflow_set_env_value "${ENV_FILE}" "DOCFLOW_ACCESS_HOST_AUTO" "${AUTO_DETECT}"
docflow_set_env_value "${ENV_FILE}" "GATEWAY_SERVER_NAME" "${ACCESS_HOST}"
docflow_set_env_value "${ENV_FILE}" "GATEWAY_TLS_CN" "${ACCESS_HOST}"
docflow_set_env_value "${ENV_FILE}" "GATEWAY_EXTERNAL_HTTPS_PORT" "${HTTPS_PORT}"
docflow_set_env_value "${ENV_FILE}" "GATEWAY_EXTERNAL_HTTP_SUFFIX" "${HTTP_SUFFIX}"
docflow_set_env_value "${ENV_FILE}" "GATEWAY_EXTERNAL_HTTPS_SUFFIX" "${HTTPS_SUFFIX}"
docflow_set_env_value "${ENV_FILE}" "GATEWAY_EXTERNAL_HTTPS_SUFFIX_ESCAPED" "${HTTPS_SUFFIX_ESCAPED}"
docflow_set_env_value "${ENV_FILE}" "RUKOVODITEL_PUBLIC_URL" "${PUBLIC_BASE}"
docflow_set_env_value "${ENV_FILE}" "NAUDOC_PUBLIC_URL" "${PUBLIC_BASE}/docs"
docflow_set_env_value "${ENV_FILE}" "DOCSPACE_PUBLIC_URL" "${PUBLIC_BASE}/docspace"
docflow_set_env_value "${ENV_FILE}" "WORKSPACE_PUBLIC_URL" "${PUBLIC_BASE}/workspace"
docflow_set_env_value "${ENV_FILE}" "ONLYOFFICE_PUBLIC_JS_API_URL" "${PUBLIC_BASE}/office/web-apps/apps/api/documents/api.js"

echo "[access-host] env file: ${ENV_FILE}"
echo "[access-host] host: ${ACCESS_HOST}"
echo "[access-host] platform: ${PUBLIC_BASE}/"
