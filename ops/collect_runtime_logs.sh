#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/.tmp_e2e/logs"
mkdir -p "${OUT_DIR}"

timestamp="$(date +%Y%m%d-%H%M%S)"

docker logs --tail 300 naudoc_gateway_test > "${OUT_DIR}/gateway-${timestamp}.log" 2>&1 || true
docker logs --tail 300 onlyoffice_docs_test > "${OUT_DIR}/onlyoffice-${timestamp}.log" 2>&1 || true
docker logs --tail 300 rukovoditel_test > "${OUT_DIR}/rukovoditel-${timestamp}.log" 2>&1 || true
docker logs --tail 300 naudoc34_legacy > "${OUT_DIR}/naudoc-${timestamp}.log" 2>&1 || true
docker logs --tail 300 naudoc_bridge_test > "${OUT_DIR}/bridge-${timestamp}.log" 2>&1 || true

echo "[logs] saved to ${OUT_DIR}"
