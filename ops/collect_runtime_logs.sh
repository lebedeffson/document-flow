#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/.tmp_e2e/logs"
mkdir -p "${OUT_DIR}"

# shellcheck source=lib/runtime_env.sh
source "${ROOT_DIR}/ops/lib/runtime_env.sh"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

timestamp="$(date +%Y%m%d-%H%M%S)"

docker logs --tail 300 "${GATEWAY_CONTAINER_NAME}" > "${OUT_DIR}/gateway-${timestamp}.log" 2>&1 || true
docker logs --tail 300 "${ONLYOFFICE_CONTAINER_NAME}" > "${OUT_DIR}/onlyoffice-${timestamp}.log" 2>&1 || true
docker logs --tail 300 "${RUKOVODITEL_CONTAINER_NAME}" > "${OUT_DIR}/rukovoditel-${timestamp}.log" 2>&1 || true
docker logs --tail 300 "${NAUDOC_LEGACY_CONTAINER}" > "${OUT_DIR}/naudoc-${timestamp}.log" 2>&1 || true
docker logs --tail 300 "${BRIDGE_CONTAINER}" > "${OUT_DIR}/bridge-${timestamp}.log" 2>&1 || true

echo "[logs] saved to ${OUT_DIR}"
