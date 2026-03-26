#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_CONTAINER="rukovoditel_test"

docker exec "$APP_CONTAINER" php /var/www/html/scripts/prepare_customer_demo.php

bash "$ROOT_DIR/sync_service_requests.sh"
bash "$ROOT_DIR/sync_project_documents.sh"
bash "$ROOT_DIR/pull_bridge_updates.sh" --only-linked

echo
echo "Customer demo contour prepared."
echo "Open: https://localhost:18443/"
