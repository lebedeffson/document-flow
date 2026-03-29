#!/bin/sh
set -eu

CERT_DIR="/etc/nginx/certs"
CERT_FILE="${CERT_DIR}/dms.crt"
KEY_FILE="${CERT_DIR}/dms.key"
TLS_CN="${TLS_CN:-${SERVER_NAME:-localhost}}"
TLS_DAYS="${TLS_DAYS:-825}"
TLS_SAN_PRIMARY="DNS:${TLS_CN}"

if printf '%s' "${TLS_CN}" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'; then
  TLS_SAN_PRIMARY="IP:${TLS_CN}"
fi

mkdir -p "${CERT_DIR}"

if [ ! -s "${CERT_FILE}" ] || [ ! -s "${KEY_FILE}" ]; then
  echo "[gateway] generating self-signed TLS certificate for ${TLS_CN}"
  openssl req \
    -x509 \
    -nodes \
    -newkey rsa:2048 \
    -days "${TLS_DAYS}" \
    -subj "/CN=${TLS_CN}" \
    -addext "subjectAltName=${TLS_SAN_PRIMARY},DNS:localhost,IP:127.0.0.1" \
    -keyout "${KEY_FILE}" \
    -out "${CERT_FILE}"
fi
