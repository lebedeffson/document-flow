#!/usr/bin/env bash
set -euo pipefail

docker exec rukovoditel_test php /var/www/html/scripts/pull_bridge_updates.php "$@"
