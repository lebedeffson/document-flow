#!/usr/bin/env bash
set -euo pipefail

docker exec rukovoditel_test php /var/www/html/scripts/provision_test_users.php "$@"
