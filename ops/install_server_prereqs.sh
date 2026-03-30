#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  sudo bash ops/install_server_prereqs.sh

Что делает:
1. ставит базовые пакеты для bootstrap-сценария
2. поддерживает apt/dnf/yum-based Linux серверы
3. ставит Docker через get.docker.com, если Docker еще не установлен
4. включает docker.service
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

export DEBIAN_FRONTEND=noninteractive

PKG_MANAGER=""
BASE_PACKAGES=()

if command -v apt-get >/dev/null 2>&1; then
  PKG_MANAGER="apt"
  BASE_PACKAGES=(
    ca-certificates
    curl
    git
    tar
    python3
    python3-venv
    gnupg
    lsb-release
  )
elif command -v dnf >/dev/null 2>&1; then
  PKG_MANAGER="dnf"
  BASE_PACKAGES=(
    ca-certificates
    curl
    git
    tar
    python3
    shadow-utils
  )
elif command -v yum >/dev/null 2>&1; then
  PKG_MANAGER="yum"
  BASE_PACKAGES=(
    ca-certificates
    curl
    git
    tar
    python3
    shadow-utils
  )
else
  fail "supported package manager not found; expected apt-get, dnf, or yum"
fi

case "${PKG_MANAGER}" in
  apt)
    echo "[server-prereqs] apt update"
    apt-get update

    echo "[server-prereqs] install base packages"
    apt-get install -y --no-install-recommends "${BASE_PACKAGES[@]}"
    ;;
  dnf)
    echo "[server-prereqs] dnf install base packages"
    dnf install -y "${BASE_PACKAGES[@]}"
    ;;
  yum)
    echo "[server-prereqs] yum install base packages"
    yum install -y "${BASE_PACKAGES[@]}"
    ;;
esac

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
