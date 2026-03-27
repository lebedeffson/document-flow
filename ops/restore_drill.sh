#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ROOT_DIR="${PROJECT_ROOT:-$(docflow_default_root "${SCRIPT_DIR}")}"
docflow_load_env "${ROOT_DIR}"
ROOT_DIR="${PROJECT_ROOT:-${ROOT_DIR}}"
docflow_export_runtime

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="${1:-${ROOT_DIR}/backups/restore-drill-${STAMP}}"
REPORT_FILE="${ROOT_DIR}/docs/reference/RESTORE_DRILL_REPORT.md"
CHECK_LOG="/tmp/docflow-restore-drill-check.log"
SMOKE_LOG="/tmp/docflow-restore-drill-smoke.log"
READY_LOG="/tmp/docflow-restore-drill-ready.log"

echo "[drill] creating fresh backup"
"${SCRIPT_DIR}/backup_all.sh" "${BACKUP_DIR}"

echo "[drill] verifying backup contents"
"${SCRIPT_DIR}/restore_all.sh" "${BACKUP_DIR}" --verify-only

echo "[drill] restoring from fresh backup"
"${SCRIPT_DIR}/restore_all.sh" "${BACKUP_DIR}"

echo "[drill] waiting for post-restore health"
for attempt in $(seq 1 12); do
  "${SCRIPT_DIR}/check_stack.sh" >"${CHECK_LOG}" 2>&1 || true

  if python3 - > /dev/null 2>"${READY_LOG}" <<'PY'
import base64
import json
import os
import ssl
import sys
import urllib.request

ctx = ssl._create_unverified_context()
bridge_health_url = os.environ["DOCFLOW_BRIDGE_PUBLIC_BASE"] + "/health"
office_health_url = os.environ["DOCFLOW_OFFICE_PUBLIC_BASE"] + "/healthcheck"
naudoc_home_url = os.environ["DOCFLOW_DOCS_BASE"] + "/home"
naudoc_username = os.environ.get("NAUDOC_USERNAME", "admin")
naudoc_password = os.environ.get("NAUDOC_PASSWORD", "admin")
try:
    with urllib.request.urlopen(bridge_health_url, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    systems = data.get("systems", {})
    if not systems.get("naudoc", {}).get("ok"):
        raise RuntimeError("naudoc backend not ready")
    if not systems.get("rukovoditel", {}).get("ok"):
        raise RuntimeError("rukovoditel backend not ready")
    with urllib.request.urlopen(office_health_url, context=ctx, timeout=10) as resp:
        if resp.read().decode("utf-8").strip().lower() != "true":
            raise RuntimeError("onlyoffice healthcheck not ready")
    req = urllib.request.Request(naudoc_home_url)
    auth = "Basic " + base64.b64encode(f"{naudoc_username}:{naudoc_password}".encode()).decode()
    req.add_header("Authorization", auth)
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        body = resp.read().decode("utf-8", "ignore")
    if "Unauthorized" in body:
        raise RuntimeError("naudoc auth page returned unauthorized body")
except Exception as exc:
    print(str(exc), file=sys.stderr)
    sys.exit(1)
sys.exit(0)
PY
  then
    break
  fi

  if [ "${attempt}" -eq 12 ]; then
    cat "${READY_LOG}" >&2
    cat "${CHECK_LOG}" >&2
    echo "[drill] post-restore stack did not recover in time" >&2
    exit 1
  fi

  sleep 5
done

echo "[drill] post-restore smoke"
"${SCRIPT_DIR}/smoke_test_stack.sh" >"${SMOKE_LOG}"

cat > "${REPORT_FILE}" <<EOF
# Restore Drill Report

Дата: \`$(date -Iseconds)\`

## Результат

1. Backup создан: \`${BACKUP_DIR}\`
2. Верификация backup: \`ok\`
3. Restore из свежего backup: \`ok\`
4. Post-restore stack check: \`ok\`
5. Post-restore smoke test: \`ok\`

## Артефакты

1. Backup: \`${BACKUP_DIR}\`
2. Stack log: \`${CHECK_LOG}\`
3. Smoke log: \`${SMOKE_LOG}\`

## Комментарий

Проверка выполнена на локальном связанном контуре.  
Для hospital production следующий шаг — повторить тот же drill на staging-контуре перед первым релизом.
EOF

echo "[drill] report saved to ${REPORT_FILE}"
echo "[drill] done"
