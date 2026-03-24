#!/usr/bin/env bash
set -euo pipefail

interval="${SYNC_INTERVAL_SECONDS:-60}"

echo "[sync-worker] Starting background sync loop with interval ${interval}s"

while true; do
  echo "[sync-worker] $(date '+%Y-%m-%d %H:%M:%S') sync cycle started"

  php /var/www/html/scripts/sync_service_requests.php || true
  php /var/www/html/scripts/sync_project_documents.php || true
  php /var/www/html/scripts/pull_bridge_updates.php || true

  echo "[sync-worker] $(date '+%Y-%m-%d %H:%M:%S') sync cycle finished"
  sleep "${interval}"
done
