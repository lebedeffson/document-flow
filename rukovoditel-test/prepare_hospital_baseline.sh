#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../ops/lib/runtime_env.sh
source "${ROOT_DIR}/../ops/lib/runtime_env.sh"
docflow_load_env "${ROOT_DIR}/.."
docflow_export_runtime

echo "[baseline] refresh process model to sync env-bound field configuration..."
docker exec "${RUKOVODITEL_CONTAINER_NAME}" php /var/www/html/scripts/provision_process_model.php

docker exec "${RUKOVODITEL_CONTAINER_NAME}" php /var/www/html/scripts/prepare_hospital_baseline.php

DB_CONTAINER="${RUKOVODITEL_DB_CONTAINER}"
DB_NAME="${RUKOVODITEL_DB_NAME}"
DB_USER="${RUKOVODITEL_DB_USER}"
DB_PASS="${RUKOVODITEL_DB_PASSWORD}"

sql_value() {
  docker exec "${DB_CONTAINER}" mariadb -N -s -u"${DB_USER}" -p"${DB_PASS}" "${DB_NAME}" -e "$1" | tr -d '\r'
}

seed_reference_onlyoffice() {
  local title="$1"
  local file_name="$2"
  local line_1="$3"
  local line_2="$4"
  local line_3="$5"
  local item_id

  item_id="$(sql_value "select id from app_entity_25 where field_242='$(printf "%s" "${title}" | sed "s/'/''/g")' order by id desc limit 1;")"
  if [[ -z "${item_id}" ]]; then
    echo "[baseline] ONLYOFFICE seed skipped, document not found: ${title}" >&2
    return 1
  fi

  bash "${ROOT_DIR}/seed_onlyoffice_document.sh" "${item_id}" "${file_name}" "${line_1}" "${line_2}" "${line_3}"
}

seed_reference_onlyoffice \
  "Рабочий документ отделения: Иван Иванов" \
  "ivan-ivanov-test.docx" \
  "Рабочий документ для Ивана Иванова" \
  "Иван Иванов ведет черновик документа через ONLYOFFICE." \
  "Документ используется как контрольный рабочий кейс: открыть, найти, изменить, сохранить."

seed_reference_onlyoffice \
  "Направление пациента: Иван Иванов" \
  "patient-route-ivan-ivanov.docx" \
  "Направление пациента: Иван Иванов" \
  "Контрольный hospital-сценарий для врача и регистратуры." \
  "Документ нужен для проверки маршрута пациента, редактирования и публикации."

seed_reference_onlyoffice \
  "Медицинская запись отделения: Иван Иванов" \
  "clinical-note-ivan-ivanov.docx" \
  "Медицинская запись отделения: Иван Иванов" \
  "Контрольный hospital-сценарий для внутренней медицинской документации." \
  "Документ нужен для проверки клинического маршрута и совместной правки."

seed_reference_onlyoffice \
  "Внутренний приказ отделения: график обходов" \
  "internal-order-rounds.docx" \
  "Внутренний приказ отделения: график обходов" \
  "Контрольный сценарий для заведующего отделением." \
  "Документ нужен для проверки маршрута согласования и ознакомления персонала."

seed_reference_onlyoffice \
  "Таблица дежурств отделения: апрель 2026" \
  "duty-schedule-april-2026.xlsx" \
  "Дежурные врачи" \
  "Старшая медсестра смены" \
  "Контрольная таблица для проверки Excel-сценария в ONLYOFFICE."

bash "$ROOT_DIR/sync_service_requests.sh"
bash "$ROOT_DIR/sync_project_documents.sh"
bash "$ROOT_DIR/sync_document_cards.sh" --force-all
bash "$ROOT_DIR/pull_bridge_updates.sh" --only-linked

echo "[baseline] reapplying ecosystem models after bridge pull..."
docker exec "${RUKOVODITEL_CONTAINER_NAME}" php /var/www/html/scripts/prepare_hospital_baseline.php

echo
echo "Hospital baseline prepared."
echo "Open: ${DOCFLOW_PUBLIC_BASE}/"
