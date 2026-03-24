#!/bin/sh
set -eu

CERT_DIR="/etc/nginx/certs"
CERT_FILE="${CERT_DIR}/dms.crt"
KEY_FILE="${CERT_DIR}/dms.key"
TLS_CN="${TLS_CN:-${SERVER_NAME:-localhost}}"
TLS_DAYS="${TLS_DAYS:-825}"

mkdir -p "${CERT_DIR}"

if [ ! -s "${CERT_FILE}" ] || [ ! -s "${KEY_FILE}" ]; then
  echo "[gateway] generating self-signed TLS certificate for ${TLS_CN}"
  openssl req \
    -x509 \
    -nodes \
    -newkey rsa:2048 \
    -days "${TLS_DAYS}" \
    -subj "/CN=${TLS_CN}" \
    -addext "subjectAltName=DNS:${TLS_CN},DNS:localhost,IP:127.0.0.1" \
    -keyout "${KEY_FILE}" \
    -out "${CERT_FILE}"
fi
