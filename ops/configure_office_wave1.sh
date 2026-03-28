#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ROOT_DIR="$(docflow_default_root "${SCRIPT_DIR}")"
ENV_FILE="$(docflow_env_file_path "${ROOT_DIR}")"

docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

DOCSPACE_MODE=""
WORKSPACE_MODE=""
DOCSPACE_TARGET_VALUE="${DOCSPACE_TARGET_URL:-}"
WORKSPACE_TARGET_VALUE="${WORKSPACE_TARGET_URL:-}"
RUN_BASELINE=1
REQUIRE_LIVE_TARGETS=""

usage() {
  cat <<'EOF'
Usage:
  bash ops/configure_office_wave1.sh [options]

Options:
  --docspace-target <url>       Enable DocSpace and set external target URL
  --workspace-target <url>      Enable Workspace and set external target URL
  --docspace-shell-only         Enable DocSpace in shell-only mode (clear target URL)
  --workspace-shell-only        Enable Workspace in shell-only mode (clear target URL)
  --disable-docspace            Disable DocSpace
  --disable-workspace           Disable Workspace
  --require-live-targets        Mark Wave 1 office layer as production-ready only with real target URLs
  --allow-shell-only            Allow shell-only mode without production blocker
  --skip-baseline               Do not rerun hospital baseline after config update
  -h, --help                    Show this help
EOF
}

fail() {
  echo "[office-wave1] ERROR: $*" >&2
  exit 1
}

require_http_url() {
  local value="${1:-}"
  [[ "${value}" == http://* || "${value}" == https://* ]] || fail "expected http(s) url, got: ${value:-<empty>}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --docspace-target)
      shift
      [[ $# -gt 0 ]] || fail "missing value for --docspace-target"
      DOCSPACE_MODE="live_target"
      DOCSPACE_TARGET_VALUE="$1"
      ;;
    --workspace-target)
      shift
      [[ $# -gt 0 ]] || fail "missing value for --workspace-target"
      WORKSPACE_MODE="live_target"
      WORKSPACE_TARGET_VALUE="$1"
      ;;
    --docspace-shell-only)
      DOCSPACE_MODE="shell_only"
      DOCSPACE_TARGET_VALUE=""
      ;;
    --workspace-shell-only)
      WORKSPACE_MODE="shell_only"
      WORKSPACE_TARGET_VALUE=""
      ;;
    --disable-docspace)
      DOCSPACE_MODE="disabled"
      DOCSPACE_TARGET_VALUE=""
      ;;
    --disable-workspace)
      WORKSPACE_MODE="disabled"
      WORKSPACE_TARGET_VALUE=""
      ;;
    --require-live-targets)
      REQUIRE_LIVE_TARGETS="1"
      ;;
    --allow-shell-only)
      REQUIRE_LIVE_TARGETS="0"
      ;;
    --skip-baseline)
      RUN_BASELINE=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown option: $1"
      ;;
  esac
  shift
done

mkdir -p "$(dirname "${ENV_FILE}")"
touch "${ENV_FILE}"

docflow_set_env_value "${ENV_FILE}" "DOCSPACE_PUBLIC_URL" "$(docflow_docspace_public_base)"
docflow_set_env_value "${ENV_FILE}" "WORKSPACE_PUBLIC_URL" "$(docflow_workspace_public_base)"

apply_service_mode() {
  local service_key="${1:-}"
  local mode="${2:-}"
  local target="${3:-}"
  local enabled_key="${service_key}_ENABLED"
  local target_key="${service_key}_TARGET_URL"

  case "${mode}" in
    "")
      return 0
      ;;
    disabled)
      docflow_set_env_value "${ENV_FILE}" "${enabled_key}" "0"
      docflow_set_env_value "${ENV_FILE}" "${target_key}" ""
      ;;
    shell_only)
      docflow_set_env_value "${ENV_FILE}" "${enabled_key}" "1"
      docflow_set_env_value "${ENV_FILE}" "${target_key}" ""
      ;;
    live_target)
      require_http_url "${target}"
      docflow_set_env_value "${ENV_FILE}" "${enabled_key}" "1"
      docflow_set_env_value "${ENV_FILE}" "${target_key}" "${target}"
      ;;
    *)
      fail "unsupported mode '${mode}' for ${service_key}"
      ;;
  esac
}

apply_service_mode "DOCSPACE" "${DOCSPACE_MODE}" "${DOCSPACE_TARGET_VALUE}"
apply_service_mode "WORKSPACE" "${WORKSPACE_MODE}" "${WORKSPACE_TARGET_VALUE}"

if [[ -n "${REQUIRE_LIVE_TARGETS}" ]]; then
  docflow_set_env_value "${ENV_FILE}" "DOCFLOW_OFFICE_WAVE1_REQUIRE_LIVE_TARGETS" "${REQUIRE_LIVE_TARGETS}"
fi

docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

if [[ "${RUN_BASELINE}" == "1" ]]; then
  bash "${ROOT_DIR}/rukovoditel-test/prepare_hospital_baseline.sh"
fi

describe_mode() {
  local enabled="${1:-0}"
  local target="${2:-}"

  if [[ "${enabled}" != "1" && "${enabled,,}" != "true" && "${enabled,,}" != "yes" && "${enabled,,}" != "on" ]]; then
    printf 'disabled'
    return 0
  fi

  if [[ -n "${target}" ]]; then
    printf 'live_target'
    return 0
  fi

  printf 'shell_only'
}

echo
echo "[office-wave1] env file: ${ENV_FILE}"
echo "[office-wave1] docspace_public_url: ${DOCFLOW_DOCSPACE_PUBLIC_BASE}"
echo "[office-wave1] docspace_mode: $(describe_mode "${DOCSPACE_ENABLED:-1}" "${DOCSPACE_TARGET_URL:-}")"
echo "[office-wave1] docspace_target_url: ${DOCSPACE_TARGET_URL:-<empty>}"
echo "[office-wave1] workspace_public_url: ${DOCFLOW_WORKSPACE_PUBLIC_BASE}"
echo "[office-wave1] workspace_mode: $(describe_mode "${WORKSPACE_ENABLED:-1}" "${WORKSPACE_TARGET_URL:-}")"
echo "[office-wave1] workspace_target_url: ${WORKSPACE_TARGET_URL:-<empty>}"
echo "[office-wave1] require_live_targets: ${DOCFLOW_OFFICE_WAVE1_REQUIRE_LIVE_TARGETS:-0}"
if [[ "${RUN_BASELINE}" == "1" ]]; then
  echo "[office-wave1] hospital baseline refreshed"
fi
