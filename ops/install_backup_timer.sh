#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/home/lebedeffson/Code/Документооборот"
ROOT_DIR="${PROJECT_ROOT:-${ROOT_DIR}}"
SYSTEMD_DIR="${1:-/etc/systemd/system}"

SERVICE_SRC="${ROOT_DIR}/ops/systemd/docflow-backup.service"
TIMER_SRC="${ROOT_DIR}/ops/systemd/docflow-backup.timer"

if [ ! -f "${SERVICE_SRC}" ] || [ ! -f "${TIMER_SRC}" ]; then
  echo "[install-backup-timer] missing template files in ${ROOT_DIR}/ops/systemd" >&2
  exit 1
fi

echo "[install-backup-timer] target systemd dir: ${SYSTEMD_DIR}"
install -D -m 0644 "${SERVICE_SRC}" "${SYSTEMD_DIR}/docflow-backup.service"
install -D -m 0644 "${TIMER_SRC}" "${SYSTEMD_DIR}/docflow-backup.timer"

echo
echo "Installed:"
echo "  ${SYSTEMD_DIR}/docflow-backup.service"
echo "  ${SYSTEMD_DIR}/docflow-backup.timer"
echo
echo "Next steps on the target server:"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable --now docflow-backup.timer"
echo "  systemctl status docflow-backup.timer"
