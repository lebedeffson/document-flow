#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ENV_FILE="$(docflow_env_file_path "${ROOT_DIR}")"

usage() {
  echo "Usage: bash ops/show_access_points.sh [--env-file <path>]"
}

while [ "$#" -gt 0 ]; do
  case "${1}" in
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
      echo "[access-points] unknown argument: ${1}" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [ ! -f "${ENV_FILE}" ]; then
  echo "[access-points] missing env file: ${ENV_FILE}" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
. "${ENV_FILE}"
set +a

export DOCFLOW_ACCESS_HOST="${DOCFLOW_ACCESS_HOST:-${GATEWAY_SERVER_NAME:-}}"
docflow_export_runtime

ACCESS_REPORT_PATH="${DOCFLOW_ACCESS_REPORT_PATH:-runtime/monitoring/access_points.txt}"
if [[ "${ACCESS_REPORT_PATH}" != /* ]]; then
  ACCESS_REPORT_PATH="${ROOT_DIR}/${ACCESS_REPORT_PATH}"
fi

mkdir -p "$(dirname "${ACCESS_REPORT_PATH}")"

PRIMARY_IP="$(docflow_detect_primary_ipv4 || true)"
ALL_IPS="$(docflow_list_non_loopback_ipv4s | awk 'NF' | paste -sd ',' - | sed 's/,/, /g')"

MAIN_ALIAS_LINE=""
if [ -n "${PRIMARY_IP}" ] && [ -n "${DOCFLOW_PUBLIC_HOST:-}" ] && ! docflow_is_ipv4_literal "${DOCFLOW_PUBLIC_HOST}"; then
  MAIN_ALIAS_LINE="${PRIMARY_IP} ${DOCFLOW_PUBLIC_HOST}"
fi

DOCSPACE_TARGET_HOST=""
if [ -n "${DOCSPACE_TARGET_URL:-}" ]; then
  DOCSPACE_TARGET_HOST="$(docflow_url_field "${DOCSPACE_TARGET_URL}" host)"
fi

WORKSPACE_TARGET_HOST=""
if [ -n "${WORKSPACE_TARGET_URL:-}" ]; then
  WORKSPACE_TARGET_HOST="$(docflow_url_field "${WORKSPACE_TARGET_URL}" host)"
fi

DOCSPACE_SAME_HOST_PROXY=0
if [ -n "${DOCSPACE_TARGET_HOST}" ] && docflow_is_internal_gateway_target_host "${DOCSPACE_TARGET_HOST}"; then
  DOCSPACE_SAME_HOST_PROXY=1
fi

WORKSPACE_SAME_HOST_PROXY=0
if [ -n "${WORKSPACE_TARGET_HOST}" ] && docflow_is_internal_gateway_target_host "${WORKSPACE_TARGET_HOST}"; then
  WORKSPACE_SAME_HOST_PROXY=1
fi

workspace_community_enabled="${DOCFLOW_WORKSPACE_WAVE1_ENABLE_COMMUNITY:-0}"

docspace_mode="shell_only"
if [ "${DOCSPACE_ENABLED:-1}" != "1" ]; then
  docspace_mode="disabled"
elif [ -n "${DOCSPACE_TARGET_URL:-}" ]; then
  docspace_mode="live_target"
fi

workspace_mode="shell_only"
if [ "${WORKSPACE_ENABLED:-1}" != "1" ]; then
  workspace_mode="disabled"
elif [ -n "${WORKSPACE_TARGET_URL:-}" ]; then
  workspace_mode="live_target"
fi

{
  echo "DocFlow access points"
  echo "Generated: $(date -Iseconds)"
  echo
  echo "Selected access host: ${DOCFLOW_PUBLIC_HOST:-<unset>}"
  echo "Detected server IPv4: ${PRIMARY_IP:-<not found>}"
  echo "Other server IPv4s: ${ALL_IPS:-<none>}"
  echo
  echo "Main platform: ${DOCFLOW_PUBLIC_BASE}/"
  echo "Rukovoditel UI: ${DOCFLOW_PUBLIC_BASE}/"
  echo "Bridge: ${DOCFLOW_BRIDGE_PUBLIC_BASE}/"
  echo "NauDoc: ${DOCFLOW_DOCS_BASE}/"
  echo "ONLYOFFICE Docs: ${DOCFLOW_OFFICE_PUBLIC_BASE}/"
  echo "DocSpace frontdoor: ${DOCFLOW_DOCSPACE_PUBLIC_BASE}/"
  echo "DocSpace Collaboration entry: ${DOCFLOW_DOCSPACE_PUBLIC_BASE}/?room_type=collaboration_room"
  echo "DocSpace Public entry: ${DOCFLOW_DOCSPACE_PUBLIC_BASE}/?room_type=public_room"
  echo "DocSpace Form filling entry: ${DOCFLOW_DOCSPACE_PUBLIC_BASE}/?room_type=form_filling_room"
  echo "Workspace frontdoor: ${DOCFLOW_WORKSPACE_PUBLIC_BASE}/"
  echo "Workspace Calendar entry: ${DOCFLOW_WORKSPACE_PUBLIC_BASE}/?module=calendar"
  if [ "${workspace_community_enabled}" = "1" ]; then
    echo "Workspace Community entry: ${DOCFLOW_WORKSPACE_PUBLIC_BASE}/?module=community"
  fi
  echo
  echo "DocSpace mode: ${docspace_mode}"
  if [ -n "${DOCSPACE_TARGET_URL:-}" ]; then
    echo "DocSpace live target: ${DOCSPACE_TARGET_URL}"
    if [ "${DOCSPACE_SAME_HOST_PROXY}" = "1" ]; then
      echo "DocSpace proxy mode: same-host reverse proxy through ${DOCFLOW_DOCSPACE_PUBLIC_BASE}/"
    fi
  else
    echo "DocSpace live target: <not configured, works through frontdoor shell>"
  fi
  if [ -n "${DOCSPACE_COLLABORATION_ROOM_TARGET_URL:-}" ]; then
    echo "DocSpace collaboration target: ${DOCSPACE_COLLABORATION_ROOM_TARGET_URL}"
  fi
  if [ -n "${DOCSPACE_PUBLIC_ROOM_TARGET_URL:-}" ]; then
    echo "DocSpace public target: ${DOCSPACE_PUBLIC_ROOM_TARGET_URL}"
  fi
  if [ -n "${DOCSPACE_FORM_FILLING_ROOM_TARGET_URL:-}" ]; then
    echo "DocSpace form filling target: ${DOCSPACE_FORM_FILLING_ROOM_TARGET_URL}"
  fi
  echo
  echo "Workspace mode: ${workspace_mode}"
  if [ -n "${WORKSPACE_TARGET_URL:-}" ]; then
    echo "Workspace live target: ${WORKSPACE_TARGET_URL}"
    if [ "${WORKSPACE_SAME_HOST_PROXY}" = "1" ]; then
      echo "Workspace proxy mode: same-host reverse proxy through ${DOCFLOW_WORKSPACE_PUBLIC_BASE}/"
    fi
  else
    echo "Workspace live target: <not configured, works through frontdoor shell>"
  fi
  if [ -n "${WORKSPACE_CALENDAR_TARGET_URL:-}" ]; then
    echo "Workspace calendar target: ${WORKSPACE_CALENDAR_TARGET_URL}"
  fi
  if [ -n "${WORKSPACE_COMMUNITY_TARGET_URL:-}" ]; then
    echo "Workspace community target: ${WORKSPACE_COMMUNITY_TARGET_URL}"
  fi
  echo "Workspace community enabled: ${workspace_community_enabled}"
  echo
  echo "User entry address:"
  echo "  ${DOCFLOW_PUBLIC_BASE}/"
  echo
  echo "Hosts line for workstations:"
  if [ -n "${MAIN_ALIAS_LINE}" ]; then
    echo "  ${MAIN_ALIAS_LINE}"
  elif [ -n "${PRIMARY_IP}" ]; then
    echo "  ${PRIMARY_IP} <your-local-alias>"
  else
    echo "  <server-ip> ${DOCFLOW_PUBLIC_HOST:-docflow.local}"
  fi
  if [ -n "${DOCSPACE_TARGET_HOST}" ] && ! docflow_is_ipv4_literal "${DOCSPACE_TARGET_HOST}" && ! docflow_is_internal_gateway_target_host "${DOCSPACE_TARGET_HOST}" && [ "${DOCSPACE_TARGET_HOST}" != "${DOCFLOW_PUBLIC_HOST:-}" ]; then
    echo "  <docspace-ip> ${DOCSPACE_TARGET_HOST}"
  fi
  if [ -n "${WORKSPACE_TARGET_HOST}" ] && ! docflow_is_ipv4_literal "${WORKSPACE_TARGET_HOST}" && ! docflow_is_internal_gateway_target_host "${WORKSPACE_TARGET_HOST}" && [ "${WORKSPACE_TARGET_HOST}" != "${DOCFLOW_PUBLIC_HOST:-}" ]; then
    echo "  <workspace-ip> ${WORKSPACE_TARGET_HOST}"
  fi
  echo
  echo "Important:"
  echo "  - hosts on the server affect only the server itself"
  echo "  - for all workstations to open a name, use DNS or deploy hosts entries on each PC"
  echo "  - without DNS/hosts, users can open the platform by raw server IP if the certificate policy allows it"
  if [ "${DOCSPACE_SAME_HOST_PROXY}" = "1" ] || [ "${WORKSPACE_SAME_HOST_PROXY}" = "1" ]; then
    echo "  - same-host office proxy mode does not require separate workstation aliases for DocSpace/Workspace"
  fi
} | tee "${ACCESS_REPORT_PATH}"

echo "[access-points] report saved to ${ACCESS_REPORT_PATH}"
