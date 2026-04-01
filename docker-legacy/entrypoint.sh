#!/usr/bin/env bash
set -euo pipefail

INSTANCE_HOME="${INSTANCE_HOME:-/opt/naudoc}"
PY24_BIN="/opt/python2.4/bin/python2.4"
MX_BASE_VERSION="3.2.9"
NAUDOC_USERNAME="${NAUDOC_USERNAME:-admin}"
NAUDOC_PASSWORD="${NAUDOC_PASSWORD:-admin}"

if [ -d /mnt/naudoc/Products ]; then
  echo "[entrypoint] Syncing Products"
  rm -rf "${INSTANCE_HOME}/Products"
  mkdir -p "${INSTANCE_HOME}/Products"
  rsync -a /mnt/naudoc/Products/ "${INSTANCE_HOME}/Products/"
fi

if [ -d /mnt/naudoc/zopeedit ]; then
  echo "[entrypoint] Syncing zopeedit"
  rm -rf "${INSTANCE_HOME}/lib/python/zopeedit"
  mkdir -p "${INSTANCE_HOME}/lib/python"
  rsync -a /mnt/naudoc/zopeedit/ "${INSTANCE_HOME}/lib/python/zopeedit/"
fi

mkdir -p "${INSTANCE_HOME}/var"

if [ ! -f "${INSTANCE_HOME}/var/Data.fs" ] && [ -f /mnt/naudoc/var/Data.fs ]; then
  echo "[entrypoint] Seeding Data.fs"
  cp /mnt/naudoc/var/Data.fs "${INSTANCE_HOME}/var/Data.fs"
fi

if [ -n "${NAUDOC_USERNAME}" ] && [ -n "${NAUDOC_PASSWORD}" ]; then
  echo "[entrypoint] Writing inituser for ${NAUDOC_USERNAME}"
  "${PY24_BIN}" - "${INSTANCE_HOME}/inituser" "${NAUDOC_USERNAME}" "${NAUDOC_PASSWORD}" <<'PY'
import binascii
import os
import sha
import sys

inituser_path, username, password = sys.argv[1:4]
digest = binascii.b2a_base64(sha.new(password).digest())[:-1]
handle = open(inituser_path, 'w')
handle.write('%s:{SHA}%s\n' % (username, digest))
handle.close()
os.chmod(inituser_path, 0644)
PY
fi

if ! "${PY24_BIN}" -c "import mx.DateTime" >/dev/null 2>&1; then
  echo "[entrypoint] Installing egenix-mx-base ${MX_BASE_VERSION}"
  cd /tmp
  rm -rf "egenix-mx-base-${MX_BASE_VERSION}" "egenix-mx-base-${MX_BASE_VERSION}.tar.gz"
  curl -fsSLO "https://downloads.egenix.com/python/egenix-mx-base-${MX_BASE_VERSION}.tar.gz"
  tar -xzf "egenix-mx-base-${MX_BASE_VERSION}.tar.gz"
  cd "egenix-mx-base-${MX_BASE_VERSION}"
  "${PY24_BIN}" setup.py install
fi

if [ -d "${INSTANCE_HOME}/Products/LDAPUserFolder" ] && ! "${PY24_BIN}" -c "import ldap" >/dev/null 2>&1; then
  echo "[entrypoint] Removing LDAPUserFolder (python-ldap not available)"
  rm -rf "${INSTANCE_HOME}/Products/LDAPUserFolder"
fi

if [ -d "${INSTANCE_HOME}/Products/TextIndexNG2" ]; then
  echo "[entrypoint] Building TextIndexNG2 with $("${PY24_BIN}" -V 2>&1)"
  cd "${INSTANCE_HOME}/Products/TextIndexNG2"
  "${PY24_BIN}" setup.py build
  "${PY24_BIN}" setup.py install
fi

cd "${INSTANCE_HOME}"
echo "[entrypoint] Starting Zope instance"
exec "${INSTANCE_HOME}/bin/zopectl" fg
