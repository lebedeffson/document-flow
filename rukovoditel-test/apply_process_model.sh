#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../ops/lib/runtime_env.sh
source "${ROOT_DIR}/ops/lib/runtime_env.sh"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

docker exec "${RUKOVODITEL_CONTAINER_NAME}" php /var/www/html/scripts/provision_process_model.php
