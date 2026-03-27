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

echo "[check] containers"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo
echo "[check] gateway http -> https redirect"
redirect_headers="$(mktemp)"
curl -sS -I --max-time 10 -D "${redirect_headers}" -o /dev/null "${DOCFLOW_HTTP_BASE}" || fail "gateway http redirect is unavailable"
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
gateway_body="$(curl -k -sS -f --max-time 10 "${DOCFLOW_PUBLIC_BASE}/healthz")" || fail "gateway /healthz failed"
printf '%s\n' "${gateway_body}"
if [[ "${gateway_body}" != "ok" ]]; then
  fail "gateway /healthz returned unexpected body: ${gateway_body}"
fi

echo
echo "[check] middleware health through gateway"
bridge_health="$(curl -k -sS -f --max-time 10 "${DOCFLOW_BRIDGE_PUBLIC_BASE}/health")" || fail "bridge /health failed"
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
onlyoffice_body="$(curl -k -sS -f --max-time 10 "${DOCFLOW_OFFICE_PUBLIC_BASE}/healthcheck")" || fail "onlyoffice /healthcheck failed"
printf '%s\n' "${onlyoffice_body}"
if [[ "${onlyoffice_body}" != "true" ]]; then
  fail "onlyoffice /healthcheck returned unexpected body: ${onlyoffice_body}"
fi
