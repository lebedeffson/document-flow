#!/usr/bin/env bash
set -euo pipefail

INSTANCE_HOME="${INSTANCE_HOME:-/opt/naudoc}"

echo "[entrypoint] Starting Zope instance at $INSTANCE_HOME"
exec "$INSTANCE_HOME/bin/zopectl" fg
