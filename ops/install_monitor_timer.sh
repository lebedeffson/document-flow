#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SYSTEMD_DIR="${1:-/etc/systemd/system}"

SERVICE_SRC="${ROOT_DIR}/ops/systemd/docflow-monitor.service"
TIMER_SRC="${ROOT_DIR}/ops/systemd/docflow-monitor.timer"

if [ ! -f "${SERVICE_SRC}" ] || [ ! -f "${TIMER_SRC}" ]; then
  echo "[install-monitor-timer] missing template files in ${ROOT_DIR}/ops/systemd" >&2
  exit 1
fi

echo "[install-monitor-timer] target systemd dir: ${SYSTEMD_DIR}"
install -Dm644 "${SERVICE_SRC}" "${SYSTEMD_DIR}/docflow-monitor.service"
install -Dm644 "${TIMER_SRC}" "${SYSTEMD_DIR}/docflow-monitor.timer"

echo "[install-monitor-timer] installed:"
echo "  ${SYSTEMD_DIR}/docflow-monitor.service"
echo "  ${SYSTEMD_DIR}/docflow-monitor.timer"
echo
echo "Next steps:"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable --now docflow-monitor.timer"
