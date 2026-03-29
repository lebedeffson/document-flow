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
DOCSPACE_COLLABORATION_TARGET_VALUE=""
DOCSPACE_PUBLIC_TARGET_VALUE=""
DOCSPACE_FORM_FILLING_TARGET_VALUE=""
WORKSPACE_CALENDAR_TARGET_VALUE=""
WORKSPACE_COMMUNITY_TARGET_VALUE=""
WORKSPACE_COMMUNITY_VALUE=""
RUN_BASELINE=1
REQUIRE_LIVE_TARGETS=""

usage() {
  cat <<'EOF'
Usage:
  bash ops/configure_office_wave1.sh [options]

Options:
  --docspace-target <url>       Enable DocSpace and set live target URL
  --workspace-target <url>      Enable Workspace and set live target URL
  --docspace-collaboration-target <url>
                                Set target URL for Collaboration rooms
  --docspace-public-target <url>
                                Set target URL for Public rooms
  --docspace-form-filling-target <url>
                                Set target URL for Form filling rooms
  --workspace-calendar-target <url>
                                Set target URL for Calendar
  --workspace-community-target <url>
                                Set target URL for Community
  --docspace-shell-only         Enable DocSpace in shell-only mode (clear target URL)
  --workspace-shell-only        Enable Workspace in shell-only mode (clear target URL)
  --disable-docspace            Disable DocSpace
  --disable-workspace           Disable Workspace
  --workspace-calendar-only     Keep only Calendar in Workspace Wave 1 and hide Community
  --workspace-with-community    Keep Calendar and expose Community in Workspace Wave 1
  --require-live-targets        Mark Wave 1 office layer as production-ready only with live target URLs
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
    --docspace-collaboration-target)
      shift
      [[ $# -gt 0 ]] || fail "missing value for --docspace-collaboration-target"
      DOCSPACE_COLLABORATION_TARGET_VALUE="$1"
      ;;
    --docspace-public-target)
      shift
      [[ $# -gt 0 ]] || fail "missing value for --docspace-public-target"
      DOCSPACE_PUBLIC_TARGET_VALUE="$1"
      ;;
    --docspace-form-filling-target)
      shift
      [[ $# -gt 0 ]] || fail "missing value for --docspace-form-filling-target"
      DOCSPACE_FORM_FILLING_TARGET_VALUE="$1"
      ;;
    --workspace-calendar-target)
      shift
      [[ $# -gt 0 ]] || fail "missing value for --workspace-calendar-target"
      WORKSPACE_CALENDAR_TARGET_VALUE="$1"
      ;;
    --workspace-community-target)
      shift
      [[ $# -gt 0 ]] || fail "missing value for --workspace-community-target"
      WORKSPACE_COMMUNITY_TARGET_VALUE="$1"
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
    --workspace-calendar-only)
      WORKSPACE_COMMUNITY_VALUE="0"
      ;;
    --workspace-with-community)
      WORKSPACE_COMMUNITY_VALUE="1"
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

apply_optional_target() {
  local env_key="${1:-}"
  local value="${2:-}"

  if [[ -z "${env_key}" || -z "${value}" ]]; then
    return 0
  fi

  require_http_url "${value}"
  docflow_set_env_value "${ENV_FILE}" "${env_key}" "${value}"
}

clear_env_values() {
  local env_file="${1:-}"
  shift || true

  local env_key=""
  for env_key in "$@"; do
    [[ -n "${env_key}" ]] || continue
    docflow_set_env_value "${env_file}" "${env_key}" ""
  done
}

if [[ "${DOCSPACE_MODE}" == "shell_only" || "${DOCSPACE_MODE}" == "disabled" ]]; then
  clear_env_values "${ENV_FILE}" \
    "DOCSPACE_COLLABORATION_ROOM_TARGET_URL" \
    "DOCSPACE_PUBLIC_ROOM_TARGET_URL" \
    "DOCSPACE_FORM_FILLING_ROOM_TARGET_URL"
fi

if [[ "${WORKSPACE_MODE}" == "shell_only" || "${WORKSPACE_MODE}" == "disabled" ]]; then
  clear_env_values "${ENV_FILE}" \
    "WORKSPACE_CALENDAR_TARGET_URL" \
    "WORKSPACE_COMMUNITY_TARGET_URL"
fi

apply_optional_target "DOCSPACE_COLLABORATION_ROOM_TARGET_URL" "${DOCSPACE_COLLABORATION_TARGET_VALUE}"
apply_optional_target "DOCSPACE_PUBLIC_ROOM_TARGET_URL" "${DOCSPACE_PUBLIC_TARGET_VALUE}"
apply_optional_target "DOCSPACE_FORM_FILLING_ROOM_TARGET_URL" "${DOCSPACE_FORM_FILLING_TARGET_VALUE}"
apply_optional_target "WORKSPACE_CALENDAR_TARGET_URL" "${WORKSPACE_CALENDAR_TARGET_VALUE}"
apply_optional_target "WORKSPACE_COMMUNITY_TARGET_URL" "${WORKSPACE_COMMUNITY_TARGET_VALUE}"

if [[ -n "${WORKSPACE_COMMUNITY_VALUE}" ]]; then
  docflow_set_env_value "${ENV_FILE}" "DOCFLOW_WORKSPACE_WAVE1_ENABLE_COMMUNITY" "${WORKSPACE_COMMUNITY_VALUE}"

  if [[ "${WORKSPACE_COMMUNITY_VALUE}" == "0" ]]; then
    clear_env_values "${ENV_FILE}" "WORKSPACE_COMMUNITY_TARGET_URL"
  fi
fi

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
echo "[office-wave1] docspace_collaboration_target_url: ${DOCSPACE_COLLABORATION_ROOM_TARGET_URL:-<empty>}"
echo "[office-wave1] docspace_public_target_url: ${DOCSPACE_PUBLIC_ROOM_TARGET_URL:-<empty>}"
echo "[office-wave1] docspace_form_filling_target_url: ${DOCSPACE_FORM_FILLING_ROOM_TARGET_URL:-<empty>}"
echo "[office-wave1] workspace_public_url: ${DOCFLOW_WORKSPACE_PUBLIC_BASE}"
echo "[office-wave1] workspace_mode: $(describe_mode "${WORKSPACE_ENABLED:-1}" "${WORKSPACE_TARGET_URL:-}")"
echo "[office-wave1] workspace_target_url: ${WORKSPACE_TARGET_URL:-<empty>}"
echo "[office-wave1] workspace_calendar_target_url: ${WORKSPACE_CALENDAR_TARGET_URL:-<empty>}"
echo "[office-wave1] workspace_community_target_url: ${WORKSPACE_COMMUNITY_TARGET_URL:-<empty>}"
echo "[office-wave1] workspace_calendar_enabled: 1"
echo "[office-wave1] workspace_community_enabled: ${DOCFLOW_WORKSPACE_WAVE1_ENABLE_COMMUNITY:-0}"
echo "[office-wave1] require_live_targets: ${DOCFLOW_OFFICE_WAVE1_REQUIRE_LIVE_TARGETS:-0}"
if [[ "${RUN_BASELINE}" == "1" ]]; then
  echo "[office-wave1] hospital baseline refreshed"
fi
