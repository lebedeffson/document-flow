#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=./lib/runtime_env.sh
source "${ROOT_DIR}/ops/lib/runtime_env.sh"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

OUT_DIR="${ROOT_DIR}/runtime/monitoring"
OUT_FILE="${OUT_DIR}/START_HERE.txt"
PRIMARY_IP="$(docflow_detect_primary_ipv4 || true)"

mkdir -p "${OUT_DIR}"

cat > "${OUT_FILE}" <<EOF
DOCFLOW QUICK START
Generated: $(date '+%Y-%m-%d %H:%M:%S %Z')

1. MAIN ADDRESS
${DOCFLOW_PUBLIC_BASE}/

2. OTHER ADDRESSES
NauDoc: ${NAUDOC_PUBLIC_URL}
Bridge: ${DOCFLOW_BRIDGE_PUBLIC_BASE}
ONLYOFFICE Docs: ${DOCFLOW_OFFICE_PUBLIC_BASE}
DocSpace: ${DOCSPACE_PUBLIC_URL}
Workspace: ${WORKSPACE_PUBLIC_URL}

3. SERVER IP
${PRIMARY_IP:-<not detected>}

4. LOGIN / PASSWORD
admin / ${DOCFLOW_ADMIN_PASSWORD}
${DOCFLOW_MANAGER_USERNAME} / ${DOCFLOW_ROLE_DEFAULT_PASSWORD}
${DOCFLOW_EMPLOYEE_USERNAME} / ${DOCFLOW_ROLE_DEFAULT_PASSWORD}
${DOCFLOW_NURSE_USERNAME} / ${DOCFLOW_ROLE_DEFAULT_PASSWORD}
${DOCFLOW_REQUESTER_USERNAME} / ${DOCFLOW_ROLE_DEFAULT_PASSWORD}
${DOCFLOW_OFFICE_USERNAME} / ${DOCFLOW_ROLE_DEFAULT_PASSWORD}

5. WHAT TO CHECK FIRST
1. Open ${DOCFLOW_PUBLIC_BASE}/
2. Login as ${DOCFLOW_EMPLOYEE_USERNAME}
3. Open a Word document and save changes
4. Login as ${DOCFLOW_MANAGER_USERNAME} or ${DOCFLOW_NURSE_USERNAME}
5. Open an Excel table and save changes
6. Open ${DOCSPACE_PUBLIC_URL}
7. Open ${WORKSPACE_PUBLIC_URL}?workspace_module=calendar

6. USEFUL FILES ON SERVER
Access points: ${ROOT_DIR}/runtime/monitoring/access_points.txt
LAN test packet: ${ROOT_DIR}/.tmp_lan_manual_test/LAN_MANUAL_TEST_PACKET.md
Install summary: ${ROOT_DIR}/runtime/monitoring/install_everything_summary.txt

7. QUICK COMMANDS
cat ${ROOT_DIR}/runtime/monitoring/START_HERE.txt
cat ${ROOT_DIR}/runtime/monitoring/access_points.txt
cd ${ROOT_DIR} && bash ops/check_stack.sh
cd ${ROOT_DIR} && bash ops/day1_week1_acceptance.sh --skip-deep-audit
EOF

echo "Created ${OUT_FILE}"
