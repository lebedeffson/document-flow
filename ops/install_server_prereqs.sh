#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  sudo bash ops/install_server_prereqs.sh

Что делает:
1. ставит базовые пакеты для bootstrap-сценария
2. ставит Docker через get.docker.com, если Docker еще не установлен
3. включает docker.service
EOF
}

fail() {
  echo "[server-prereqs] ERROR: $*" >&2
  exit 1
}

require_root() {
  [ "$(id -u)" -eq 0 ] || fail "root is required; run with sudo"
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

require_root

command -v apt-get >/dev/null 2>&1 || fail "only apt-based Debian/Ubuntu servers are supported by this bootstrap helper"

export DEBIAN_FRONTEND=noninteractive

echo "[server-prereqs] apt update"
apt-get update

echo "[server-prereqs] install base packages"
apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  git \
  tar \
  python3 \
  python3-venv \
  gnupg \
  lsb-release

if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
  echo "[server-prereqs] install docker"
  curl -fsSL https://get.docker.com | sh
fi

if command -v systemctl >/dev/null 2>&1; then
  systemctl enable --now docker || true
fi

if [ -n "${SUDO_USER:-}" ] && [ "${SUDO_USER}" != "root" ]; then
  usermod -aG docker "${SUDO_USER}" || true
fi

echo "[server-prereqs] done"
