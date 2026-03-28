#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"

ROOT_DIR="$(docflow_default_root "${SCRIPT_DIR}")"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

STAMP="$(date +%Y%m%d-%H%M%S)"
OUTPUT_DIR="${1:-${ROOT_DIR}/runtime/pilot-packages/pilot-package-${STAMP}}"

DOC_FILES=(
  "README.md"
  "USER_QUICKSTART_GUIDE.md"
  "CUSTOMER_DEMO_SCRIPT.md"
  "HOSPITAL_PRODUCTION_ROADMAP.md"
  "docs/reference/CURRENT_PLATFORM_ANALYSIS.md"
  "docs/reference/DATABASE_PRODUCTION_READINESS.md"
  "docs/reference/HOSPITAL_NEXT_STEPS_PLAN.md"
  "docs/reference/HOSPITAL_PLATFORM_GAP_MATRIX.md"
  "docs/reference/HOSPITAL_TARGET_OPERATING_MODEL.md"
  "docs/reference/OFFLINE_INSTALL_RUNBOOK.md"
  "docs/reference/STAGING_RUNBOOK.md"
  "docs/reference/PILOT_RUNBOOK.md"
)

SCREENSHOT_FILES=(
  "docs/screenshots/employer/01-login.png"
  "docs/screenshots/employer/02-admin-dashboard.png"
  "docs/screenshots/employer/11-user-dashboard.png"
  "docs/screenshots/employer/15-user-documents.png"
  "docs/screenshots/employer/16-user-document-card.png"
  "docs/screenshots/employer/19-onlyoffice-editor.png"
  "docs/screenshots/employer/20-naudoc-home.png"
  "docs/screenshots/employer/23-bridge-overview.png"
)

mkdir -p "${OUTPUT_DIR}/docs" "${OUTPUT_DIR}/screenshots"

copy_relative_file() {
  local relative_path="${1:-}"
  if [ ! -f "${ROOT_DIR}/${relative_path}" ]; then
    echo "[pilot] missing required file: ${relative_path}" >&2
    exit 1
  fi

  mkdir -p "${OUTPUT_DIR}/$(dirname "${relative_path}")"
  cp "${ROOT_DIR}/${relative_path}" "${OUTPUT_DIR}/${relative_path}"
}

for relative_path in "${DOC_FILES[@]}"; do
  copy_relative_file "${relative_path}"
done

for relative_path in "${SCREENSHOT_FILES[@]}"; do
  copy_relative_file "${relative_path}"
done

cat > "${OUTPUT_DIR}/PILOT_PACKAGE_README.md" <<EOF
# Pilot Package

Created: ${STAMP}

## Purpose
This package is предназначен для запуска пилота на одном подразделении больницы.

## What is included
- эксплуатационные документы
- roadmap и gap analysis
- скриншоты ключевых экранов
- quickstart для администратора и пользователя

## Main entry points
- Platform: ${DOCFLOW_PUBLIC_BASE}/
- NauDoc: ${DOCFLOW_DOCS_BASE}/
- Bridge: ${DOCFLOW_BRIDGE_PUBLIC_BASE}/

## Recommended pilot scope
1. Одно подразделение
2. Один администратор платформы
3. 3-10 врачей/сотрудников
4. Канцелярия или регистратура
5. Один-два типа документа в первом цикле

## Key docs
- README.md
- USER_QUICKSTART_GUIDE.md
- docs/reference/PILOT_RUNBOOK.md
- docs/reference/OFFLINE_INSTALL_RUNBOOK.md
- docs/reference/STAGING_RUNBOOK.md
EOF

if command -v sha256sum >/dev/null 2>&1; then
  (
    cd "${OUTPUT_DIR}"
    find . -type f ! -name 'SHA256SUMS' -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
  )
fi

echo "[pilot] ready: ${OUTPUT_DIR}"
