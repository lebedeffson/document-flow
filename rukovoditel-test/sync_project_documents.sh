#!/usr/bin/env bash
set -euo pipefail

docker exec rukovoditel_test php /var/www/html/scripts/sync_project_documents.php "$@"
