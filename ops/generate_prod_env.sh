#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ROOT_DIR="$(docflow_default_root "${SCRIPT_DIR}")"

DOMAIN="${DOCFLOW_DOMAIN:-docflow.hospital.local}"
PROJECT_ROOT_VALUE="${DOCFLOW_PROJECT_ROOT:-/opt/docflow}"
OUTPUT_FILE="${1:-${ROOT_DIR}/.env.generated.hospital}"

if [ -f "${OUTPUT_FILE}" ]; then
  echo "[env] refusing to overwrite existing file: ${OUTPUT_FILE}" >&2
  echo "[env] remove it first or pass a different output path" >&2
  exit 1
fi

DB_PASSWORD="$(docflow_random_secret 24)"
DB_ROOT_PASSWORD="$(docflow_random_secret 24)"
NAUDOC_PASSWORD="$(docflow_random_secret 24)"
BRIDGE_SYNC_CONTROL_TOKEN="$(docflow_random_secret 32)"
ONLYOFFICE_JWT_SECRET="$(docflow_random_secret 32)"

cat > "${OUTPUT_FILE}" <<EOF
# Generated on $(date -Iseconds)
# Hospital-oriented production baseline.
# Review all values before renaming this file to .env on the target server.

PROJECT_ROOT=${PROJECT_ROOT_VALUE}

# Public URLs
GATEWAY_SERVER_NAME=${DOMAIN}
GATEWAY_EXTERNAL_HTTPS_PORT=443
GATEWAY_EXTERNAL_HTTP_SUFFIX=
GATEWAY_EXTERNAL_HTTPS_SUFFIX=
GATEWAY_EXTERNAL_HTTPS_SUFFIX_ESCAPED=
GATEWAY_TLS_CN=${DOMAIN}
GATEWAY_BIND_HTTP_PORT=80
GATEWAY_BIND_HTTPS_PORT=443
RUKOVODITEL_PUBLIC_URL=https://${DOMAIN}
NAUDOC_PUBLIC_URL=https://${DOMAIN}/docs
ONLYOFFICE_PUBLIC_JS_API_URL=https://${DOMAIN}/office/web-apps/apps/api/documents/api.js

# Internal URLs
BRIDGE_BASE_URL=http://host.docker.internal:18082
RUKOVODITEL_BASE_URL=http://host.docker.internal:18081
NAUDOC_BASE_URL=http://host.docker.internal:18080/docs
SYNC_CONTROL_URL=http://host.docker.internal:18081/run_sync_job.php
ONLYOFFICE_INTEGRATION_BASE_URL=http://rukovoditel

# Gateway upstreams
GATEWAY_RUKOVODITEL_UPSTREAM=host.docker.internal:18081
GATEWAY_BRIDGE_UPSTREAM=host.docker.internal:18082
GATEWAY_NAUDOC_UPSTREAM=host.docker.internal:18080
GATEWAY_NAUDOC_UPSTREAM_ESCAPED=host.docker.internal%3A18080
GATEWAY_ONLYOFFICE_UPSTREAM=host.docker.internal:18083

# Runtime
SYNC_INTERVAL_SECONDS=60
BRIDGE_REQUEST_TIMEOUT=8
BRIDGE_DB_PATH=/data/bridge.db

# Databases and secrets
RUKOVODITEL_DB_NAME=rukovoditel
RUKOVODITEL_DB_USER=rukovoditel
RUKOVODITEL_DB_PASSWORD=${DB_PASSWORD}
RUKOVODITEL_DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
NAUDOC_USERNAME=admin
NAUDOC_PASSWORD=${NAUDOC_PASSWORD}
BRIDGE_SYNC_CONTROL_TOKEN=${BRIDGE_SYNC_CONTROL_TOKEN}
ONLYOFFICE_JWT_SECRET=${ONLYOFFICE_JWT_SECRET}

# Container names for production-like deployment
GATEWAY_CONTAINER_NAME=docflow_gateway
BRIDGE_CONTAINER=docflow_bridge
RUKOVODITEL_CONTAINER_NAME=docflow_rukovoditel
RUKOVODITEL_DB_CONTAINER=docflow_rukovoditel_db
ONLYOFFICE_CONTAINER_NAME=docflow_onlyoffice_docs
RUKOVODITEL_SYNC_WORKER_CONTAINER_NAME=docflow_sync_worker
NAUDOC_LEGACY_CONTAINER=docflow_naudoc_legacy
NAUDOC_LEGACY_COMPOSE_PROJECT=docflow_legacy
NAUDOC_LEGACY_SERVICE=naudoc_legacy
EOF

chmod 600 "${OUTPUT_FILE}" 2>/dev/null || true

echo "[env] generated: ${OUTPUT_FILE}"
echo "[env] domain: ${DOMAIN}"
echo "[env] next step: review values and rename/copy to ${ROOT_DIR}/.env on the target server"
