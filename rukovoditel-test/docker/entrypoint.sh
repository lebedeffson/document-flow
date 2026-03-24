#!/bin/sh
set -eu

mkdir -p \
  /var/www/html/uploads \
  /var/www/html/uploads/attachments \
  /var/www/html/uploads/attachments_preview \
  /var/www/html/uploads/images \
  /var/www/html/uploads/users \
  /var/www/html/uploads/onlyoffice \
  /var/www/html/uploads/file_storage \
  /var/www/html/backups \
  /var/www/html/backups/auto \
  /var/www/html/tmp \
  /var/www/html/cache \
  /var/www/html/log \
  /var/www/html/config

chown -R www-data:www-data \
  /var/www/html/config \
  /var/www/html/uploads \
  /var/www/html/backups \
  /var/www/html/tmp \
  /var/www/html/cache \
  /var/www/html/log

chmod -R 775 \
  /var/www/html/config \
  /var/www/html/uploads \
  /var/www/html/backups \
  /var/www/html/tmp \
  /var/www/html/cache \
  /var/www/html/log

exec "$@"
