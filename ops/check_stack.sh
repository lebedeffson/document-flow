#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=lib/runtime_env.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/runtime_env.sh"

ROOT_DIR="$(docflow_default_root "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

fail() {
  echo "[check] ERROR: $*" >&2
  exit 1
}

acceptable_remote_status() {
  local status="${1:-}"
  [[ "${status}" == "200" || "${status}" == "301" || "${status}" == "302" || "${status}" == "401" || "${status}" == "403" ]]
}

target_host_requires_local_probe() {
  local host="${1:-}"

  [[ "${host}" == "host.docker.internal" || "${host}" == "localhost" || "${host}" == 127.* ]]
}

curl_docflow() {
  local url="${1:-}"
  shift || true

  local scheme host port path probe_ip
  scheme="$(docflow_url_field "${url}" scheme)"
  host="$(docflow_url_field "${url}" host)"
  port="$(docflow_url_field "${url}" port)"
  path="$(docflow_url_field "${url}" path)"
  probe_ip="$(docflow_local_probe_ip)"

  if [[ -z "${scheme}" || -z "${host}" || -z "${port}" ]]; then
    echo "[check] ERROR: failed to parse url: ${url}" >&2
    return 1
  fi

  curl --resolve "${host}:${port}:${probe_ip}" "$@" "${scheme}://${host}:${port}${path}"
}

curl_target() {
  local url="${1:-}"
  shift || true

  local host port probe_ip
  host="$(docflow_url_field "${url}" host)"
  port="$(docflow_url_field "${url}" port)"
  probe_ip="$(docflow_local_probe_ip)"

  if target_host_requires_local_probe "${host}"; then
    curl --resolve "${host}:${port}:${probe_ip}" "$@" "${url}"
    return 0
  fi

  curl "$@" "${url}"
}

echo "[check] containers"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo
echo "[check] gateway http -> https redirect"
redirect_headers="$(mktemp)"
curl_docflow "${DOCFLOW_HTTP_BASE}" -sS -I --max-time 10 -D "${redirect_headers}" -o /dev/null || fail "gateway http redirect is unavailable"
cat "${redirect_headers}"
redirect_status="$(awk 'NR==1 {print $2}' "${redirect_headers}")"
redirect_location="$(awk 'BEGIN{IGNORECASE=1} /^Location:/ {print $2}' "${redirect_headers}" | tr -d '\r' | tail -n 1)"
if [[ "${redirect_status}" != "301" && "${redirect_status}" != "302" ]]; then
  fail "gateway redirect returned unexpected status ${redirect_status:-unknown}"
fi
if [[ "${redirect_location}" != https://* ]]; then
  fail "gateway redirect target is not https: ${redirect_location:-<empty>}"
fi

echo
echo "[check] gateway health"
gateway_body="$(curl_docflow "${DOCFLOW_PUBLIC_BASE}/healthz" -k -sS -f --max-time 10)" || fail "gateway /healthz failed"
printf '%s\n' "${gateway_body}"
if [[ "${gateway_body}" != "ok" ]]; then
  fail "gateway /healthz returned unexpected body: ${gateway_body}"
fi

echo
echo "[check] middleware health through gateway"
bridge_health="$(curl_docflow "${DOCFLOW_BRIDGE_PUBLIC_BASE}/health" -k -sS -f --max-time 10)" || fail "bridge /health failed"
printf '%s\n' "${bridge_health}"
python3 - "${bridge_health}" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
if payload.get("status") != "ok":
    raise SystemExit("bridge status is not ok")
systems = payload.get("systems", {})
if not systems.get("naudoc", {}).get("ok"):
    raise SystemExit("bridge reports naudoc unhealthy")
if not systems.get("rukovoditel", {}).get("ok"):
    raise SystemExit("bridge reports rukovoditel unhealthy")
PY

echo
echo "[check] onlyoffice health through gateway"
onlyoffice_body="$(curl_docflow "${DOCFLOW_OFFICE_PUBLIC_BASE}/healthcheck" -k -sS -f --max-time 10)" || fail "onlyoffice /healthcheck failed"
printf '%s\n' "${onlyoffice_body}"
if [[ "${onlyoffice_body}" != "true" ]]; then
  fail "onlyoffice /healthcheck returned unexpected body: ${onlyoffice_body}"
fi

echo
echo "[check] docspace frontdoor"
docspace_headers="$(mktemp)"
curl_docflow "${DOCFLOW_DOCSPACE_PUBLIC_BASE}/" -k -sS -I --max-time 10 -D "${docspace_headers}" -o /dev/null || fail "docspace frontdoor is unavailable"
cat "${docspace_headers}"
docspace_status="$(awk 'NR==1 {print $2}' "${docspace_headers}")"
if ! acceptable_remote_status "${docspace_status}"; then
  fail "docspace frontdoor returned unexpected status ${docspace_status:-unknown}"
fi

echo
echo "[check] workspace frontdoor"
workspace_headers="$(mktemp)"
curl_docflow "${DOCFLOW_WORKSPACE_PUBLIC_BASE}/" -k -sS -I --max-time 10 -D "${workspace_headers}" -o /dev/null || fail "workspace frontdoor is unavailable"
cat "${workspace_headers}"
workspace_status="$(awk 'NR==1 {print $2}' "${workspace_headers}")"
if ! acceptable_remote_status "${workspace_status}"; then
  fail "workspace frontdoor returned unexpected status ${workspace_status:-unknown}"
fi

if [[ -n "${DOCSPACE_TARGET_URL:-}" ]]; then
  echo
  echo "[check] docspace live target"
  docspace_target_headers="$(mktemp)"
  curl_target "${DOCSPACE_TARGET_URL}" -k -sS -I --max-time 10 -D "${docspace_target_headers}" -o /dev/null || fail "docspace live target is unavailable"
  cat "${docspace_target_headers}"
  docspace_target_status="$(awk 'NR==1 {print $2}' "${docspace_target_headers}")"
  if ! acceptable_remote_status "${docspace_target_status}"; then
    fail "docspace live target returned unexpected status ${docspace_target_status:-unknown}"
  fi
fi

if [[ -n "${WORKSPACE_TARGET_URL:-}" ]]; then
  echo
  echo "[check] workspace live target"
  workspace_target_headers="$(mktemp)"
  curl_target "${WORKSPACE_TARGET_URL}" -k -sS -I --max-time 10 -D "${workspace_target_headers}" -o /dev/null || fail "workspace live target is unavailable"
  cat "${workspace_target_headers}"
  workspace_target_status="$(awk 'NR==1 {print $2}' "${workspace_target_headers}")"
  if ! acceptable_remote_status "${workspace_target_status}"; then
    fail "workspace live target returned unexpected status ${workspace_target_status:-unknown}"
  fi
fi

check_optional_remote_target() {
  local label="${1:-}"
  local url="${2:-}"
  local headers=""
  local status=""

  [[ -n "${label}" && -n "${url}" ]] || return 0

  echo
  echo "[check] ${label}"
  headers="$(mktemp)"
  curl_target "${url}" -k -sS -I --max-time 10 -D "${headers}" -o /dev/null || fail "${label} is unavailable"
  cat "${headers}"
  status="$(awk 'NR==1 {print $2}' "${headers}")"
  if ! acceptable_remote_status "${status}"; then
    fail "${label} returned unexpected status ${status:-unknown}"
  fi
}

check_optional_remote_target "docspace collaboration target" "${DOCSPACE_COLLABORATION_ROOM_TARGET_URL:-}"
check_optional_remote_target "docspace public target" "${DOCSPACE_PUBLIC_ROOM_TARGET_URL:-}"
check_optional_remote_target "docspace form filling target" "${DOCSPACE_FORM_FILLING_ROOM_TARGET_URL:-}"
check_optional_remote_target "workspace calendar target" "${WORKSPACE_CALENDAR_TARGET_URL:-}"
check_optional_remote_target "workspace community target" "${WORKSPACE_COMMUNITY_TARGET_URL:-}"
