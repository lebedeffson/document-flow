#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=./lib/runtime_env.sh
source "${ROOT_DIR}/ops/lib/runtime_env.sh"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

OUT_DIR="${ROOT_DIR}/.tmp_lan_manual_test"
OUT_FILE="${OUT_DIR}/LAN_MANUAL_TEST_PACKET.md"
PRIMARY_IP="$( (hostname -I 2>/dev/null || true) | awk '{print $1}')"
if [[ -z "${PRIMARY_IP}" ]]; then
  PRIMARY_IP="$(ip route get 1.1.1.1 2>/dev/null | awk '/src/ {for (i = 1; i <= NF; i++) if ($i == "src") {print $(i+1); exit}}')"
fi
PUBLIC_HOST="$(printf '%s' "${DOCFLOW_PUBLIC_BASE}" | sed -E 's#https?://([^/]+)/?.*#\1#')"

mkdir -p "${OUT_DIR}"

cat > "${OUT_FILE}" <<EOF
# LAN Manual Test Packet

Дата: $(date '+%Y-%m-%d %H:%M:%S %Z')

## Вход в контур

- Основной URL: ${DOCFLOW_PUBLIC_BASE}
- NauDoc: ${NAUDOC_PUBLIC_URL}
- Bridge: ${DOCFLOW_BRIDGE_PUBLIC_BASE}
- DocSpace shell: ${DOCSPACE_PUBLIC_URL}
- Workspace shell: ${WORKSPACE_PUBLIC_URL}

## Если имя не резолвится в локальной сети

- Предпочтительно: настроить локальный DNS на имя из URL выше
- Быстрый временный вариант: добавить на рабочие станции hosts-запись
- Пример: ${PRIMARY_IP:-<LAN_IP>} ${PUBLIC_HOST}

## Учетные записи для ручной проверки

- admin / ${DOCFLOW_ADMIN_PASSWORD}
- ${DOCFLOW_MANAGER_USERNAME} / ${DOCFLOW_ROLE_DEFAULT_PASSWORD}
- ${DOCFLOW_EMPLOYEE_USERNAME} / ${DOCFLOW_ROLE_DEFAULT_PASSWORD}
- ${DOCFLOW_NURSE_USERNAME} / ${DOCFLOW_ROLE_DEFAULT_PASSWORD}
- ${DOCFLOW_REQUESTER_USERNAME} / ${DOCFLOW_ROLE_DEFAULT_PASSWORD}
- ${DOCFLOW_OFFICE_USERNAME} / ${DOCFLOW_ROLE_DEFAULT_PASSWORD}

## Что проверить руками

### 1. Word-сценарий

1. Войти под ${DOCFLOW_EMPLOYEE_USERNAME}
2. Открыть "Карточки документов"
3. Найти карточку "Рабочий документ отделения: Иван Иванов"
4. Нажать "Открыть документ в редакторе"
5. Убедиться, что открылся ONLYOFFICE редактор документа
6. Внести небольшую правку и сохранить

### 2. Excel-сценарий

1. Войти под ${DOCFLOW_MANAGER_USERNAME} или ${DOCFLOW_NURSE_USERNAME}
2. Открыть "Карточки документов"
3. Найти карточку "Таблица дежурств отделения: апрель 2026"
4. Нажать "Открыть документ в редакторе"
5. Убедиться, что открылся ONLYOFFICE редактор таблиц
6. Изменить одно из значений и сохранить

### 3. Проверка ролей

1. Под ${DOCFLOW_REQUESTER_USERNAME} убедиться, что карточки открываются без ошибок
2. Под ${DOCFLOW_OFFICE_USERNAME} проверить открытие карточки и связанных документов
3. Под admin проверить, что контур остается доступным и после пользовательских правок

## Что считать успешным результатом

- логин проходит без ошибок
- карточка документа открывается
- ONLYOFFICE открывает и Word, и Excel
- после сохранения редактор не показывает ошибок загрузки
- повторное открытие того же файла работает
- NauDoc и Bridge продолжают открываться
EOF

echo "Created ${OUT_FILE}"
