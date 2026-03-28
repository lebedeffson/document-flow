# Ops

Минимальный набор эксплуатационных скриптов для production-lite контура.

Опорный документ по доведению платформы до больничного production:

- [HOSPITAL_PRODUCTION_ROADMAP.md](/home/lebedeffson/Code/Документооборот/HOSPITAL_PRODUCTION_ROADMAP.md)

Важно для standalone-сборки подпроектов:

1. корневой `.env` должен существовать
2. при ручном `docker compose up` для отдельных каталогов лучше явно передавать:

```bash
docker compose --env-file /home/lebedeffson/Code/Документооборот/.env -f middleware/docker-compose.yml up -d --build
```

Иначе легко поднять сервис с fallback-значениями вместо актуальных production-like секретов.

## Backup

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./backup_all.sh
```

Можно указать свою папку:

```bash
./backup_all.sh /home/lebedeffson/Code/Документооборот/backups/manual-test
```

Скрипт сохраняет:

1. дамп `MariaDB`
2. `bridge.db`
3. `NauDoc Data.fs`

## Backup Timer

Для production-сервера можно поставить systemd-таймер:

```bash
cd /home/lebedeffson/Code/Документооборот
sudo ops/install_backup_timer.sh
sudo systemctl daemon-reload
sudo systemctl enable --now docflow-backup.timer
```

Шаблоны:

1. [docflow-backup.service](/home/lebedeffson/Code/Документооборот/ops/systemd/docflow-backup.service)
2. [docflow-backup.timer](/home/lebedeffson/Code/Документооборот/ops/systemd/docflow-backup.timer)

## Generate Production Env

Для hospital production можно сгенерировать candidate `.env` с безопасными секретами:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/generate_prod_env.sh
```

По умолчанию будет создан файл:

1. `/home/lebedeffson/Code/Документооборот/.env.generated.hospital`

Важно:

1. файл не коммитится
2. перед переносом на сервер его нужно проверить и переименовать в `.env`
3. по умолчанию используется домен `docflow.hospital.local`, при необходимости можно передать свой через `DOCFLOW_DOMAIN`

## Generate Staging Env

Для отдельного staging-контура теперь есть отдельный генератор:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/generate_staging_env.sh
```

По умолчанию он создает:

1. `/home/lebedeffson/Code/Документооборот/.env.generated.staging`
2. домен `staging.docflow.hospital.local`
3. отдельные bind-порты, чтобы staging не конфликтовал с production

Опорный runbook:

- [STAGING_RUNBOOK.md](/home/lebedeffson/Code/Документооборот/docs/reference/STAGING_RUNBOOK.md)

## Office Wave 1

Для `DocSpace/Workspace` первой волны теперь есть отдельный конфигурационный сценарий.

Перевести оба сервиса в рабочий `shell-only` режим и обновить baseline-ссылки:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/configure_office_wave1.sh --docspace-shell-only --workspace-shell-only
```

Подключить реальные внешние target URL:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/configure_office_wave1.sh \
  --docspace-target https://docspace.hospital.local/ \
  --workspace-target https://workspace.hospital.local/
```

Что делает скрипт:

1. обновляет `DOCSPACE/WORKSPACE` настройки в `.env`
2. фиксирует public URLs первой волны
3. при необходимости включает `shell-only` или `live_target` режим
4. по умолчанию перезаполняет baseline-ссылки в карточках, проектах, заявках и МТЗ

Проверить, хватает ли текущего host под vendor-развертывание:

```bash
cd /home/lebedeffson/Code/Документооборот
python3 ops/office_wave1_host_audit.py
```

Опорный production-runbook:

- [OFFICE_WAVE1_DEPLOYMENT.md](/home/lebedeffson/Code/Документооборот/docs/reference/OFFICE_WAVE1_DEPLOYMENT.md)

## Portable Offline Bundle

Если нужно принести платформу на флешке и развернуть на Linux-сервере без лишних ручных шагов, теперь есть отдельный bundle-сценарий.

Проверить, что bundle соберется корректно:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/create_portable_bundle.sh --verify-only --with-local-ldap
```

Собрать полный переносимый bundle:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/create_portable_bundle.sh --with-local-ldap
```

На сервере установить bundle:

```bash
cd /path/to/bundle
bash install_from_bundle.sh /opt/docflow
```

Подробный сценарий:

- [OFFLINE_INSTALL_RUNBOOK.md](/home/lebedeffson/Code/Документооборот/docs/reference/OFFLINE_INSTALL_RUNBOOK.md)

## Pilot Package

Для пилота на одном подразделении теперь можно собрать отдельный пакет документов и скриншотов:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/create_pilot_package.sh
```

Пакет складывается в `runtime/pilot-packages/...` и включает:

1. quickstart и эксплуатационные документы
2. roadmap и gap analysis
3. ключевые скриншоты платформы
4. отдельный pilot runbook

Опорный документ:

- [PILOT_RUNBOOK.md](/home/lebedeffson/Code/Документооборот/docs/reference/PILOT_RUNBOOK.md)

## Rotate NauDoc Password

Для production нельзя оставлять дефолтный пароль `NauDoc`. Теперь есть безопасный сценарий ротации:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/rotate_naudoc_password.sh
```

Что делает скрипт:

1. проверяет текущие credentials `NauDoc`
2. делает pre-rotation backup
3. меняет пароль штатным `NauDoc`-механизмом
4. обновляет `NAUDOC_PASSWORD` в `.env`
5. пересоздает зависимые контейнеры
6. валидирует новую авторизацию
7. при ошибке пытается откатиться автоматически

Важно:

1. новый пароль не печатается в stdout
2. актуальное значение остается только в `.env`
3. для явного значения можно передать пароль первым аргументом:

```bash
bash ops/rotate_naudoc_password.sh 'your-strong-password'
```

Если `.env` уже уехал вперед, а реальный текущий пароль `NauDoc` другой, можно явно передать его через override:

```bash
NAUDOC_CURRENT_PASSWORD='current-live-password' bash ops/rotate_naudoc_password.sh
```

## Restore

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./restore_all.sh /home/lebedeffson/Code/Документооборот/backups/20260324-120000
```

Проверить backup без изменения данных:

```bash
./restore_all.sh /home/lebedeffson/Code/Документооборот/backups/20260324-120000 --verify-only
```

Полный restore drill:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/restore_drill.sh
```

## Health checks

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./check_stack.sh
```

Скрипт теперь умеет честно проверять и основной контур, и staging даже без прописанного DNS, если gateway опубликован на локальные bind-порты.

## Smoke Test

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./smoke_test_stack.sh
```

Скрипт проверяет:

1. gateway и health endpoints
2. логин в `Rukovoditel`
3. публикацию `NauDoc` через `HTTPS`
4. sync-сценарии `request/project -> doc card -> bridge -> pull`
5. согласованность публичных `NauDoc`-ссылок

## Full Verification

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./run_full_verification.sh
```

Скрипт выполняет полный production-lite прогон:

1. `check_stack`
2. `smoke_test_stack`
3. синхронизацию профилей `NauDoc -> Rukovoditel`
4. `full_contour_audit`
5. аудит интеграции и `ONLYOFFICE`
6. browser e2e в `Firefox` и `Chromium`
7. глубокий browser-аудит модулей
8. сбор runtime-логов в `.tmp_e2e/logs`

## Production Readiness Audit

```bash
cd /home/lebedeffson/Code/Документооборот
python3 ops/prod_readiness_audit.py
```

Проверить candidate env без подмены текущего `.env`:

```bash
cd /home/lebedeffson/Code/Документооборот
DOCFLOW_ENV_FILE=/home/lebedeffson/Code/Документооборот/.env.generated.hospital python3 ops/prod_readiness_audit.py
```

Скрипт проверяет базовые production-риски:

1. не остались ли `localhost` и demo-public URLs
2. не используются ли дефолтные пароли и dev-secrets
3. существует ли `.env`
4. на месте ли базовые ops-скрипты

Это не заменяет полный приемочный запуск, но дает честный быстрый стоп-лист перед переносом на сервер больницы.

## Database Integrity Audit

Перед любым переносом на production и перед изменением схемы теперь нужно прогонять отдельный аудит БД:

```bash
cd /home/lebedeffson/Code/Документооборот
python3 ops/audit_database_integrity.py
```

Опорный документ:

- [DATABASE_PRODUCTION_READINESS.md](/home/lebedeffson/Code/Документооборот/docs/reference/DATABASE_PRODUCTION_READINESS.md)

## Monitoring Snapshot

Легкий monitoring baseline теперь можно получать без тяжелого стека:

```bash
cd /home/lebedeffson/Code/Документооборот
python3 ops/monitoring_snapshot.py
```

Скрипт:

1. пишет JSON-снимок состояния
2. проверяет `gateway`, `Bridge`, `ONLYOFFICE`
3. считает открытые `sync_failures`
4. показывает количество несопоставленных профилей
5. показывает свежесть последнего backup

По умолчанию snapshot сохраняется в:

- `/home/lebedeffson/Code/Документооборот/runtime/monitoring/latest_status.json`

## Local LDAP Baseline

Для `LDAP-first` стенда теперь можно поднять локальный production-like LDAP-контур отдельным профилем:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/bootstrap_local_ldap.sh
```

Что делает скрипт:

1. дописывает недостающие `LDAP_*` секреты в корневой `.env`
2. рендерит bootstrap LDIF для hospital-ролей и тестовых пользователей
3. поднимает `hospital_ldap` как отдельный compose profile `identity`
4. перенастраивает `hospital_ldap` source в `Bridge`
5. запускает `test + sync` для LDAP-каталога

Важно:

1. это не заменяет реальный `LDAP/AD` больницы
2. это production-like контур для staging/pilot и честной проверки `LDAP-first` интеграции
3. локальный LDAP поднимается отдельно и не ломает основной стек

## Monitor Timer

Для Linux-сервера можно поставить systemd-таймер мониторинга:

```bash
cd /home/lebedeffson/Code/Документооборот
sudo ops/install_monitor_timer.sh
sudo systemctl daemon-reload
sudo systemctl enable --now docflow-monitor.timer
```

Шаблоны:

1. [docflow-monitor.service](/home/lebedeffson/Code/Документооборот/ops/systemd/docflow-monitor.service)
2. [docflow-monitor.timer](/home/lebedeffson/Code/Документооборот/ops/systemd/docflow-monitor.timer)

## Identity Audit

Проверка `LDAP-first` слоя теперь есть и отдельно:

```bash
cd /home/lebedeffson/Code/Документооборот
python3 ops/audit_identity_integration.py
```

Поведение:

1. если `hospital_ldap` не активирован, audit вернет `skipped`
2. если активирован и настроен, audit проверит:
   - bind
   - sync
   - наличие обязательных LDAP-профилей

## Full Contour Audit

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./full_contour_audit.py
```

Скрипт дополнительно проверяет:

1. тестовых пользователей по ролям `руководитель / сотрудник / заявитель / канцелярия`
2. ролевой логин в `Rukovoditel` и видимость меню
3. безопасные пользовательские разделы каждой роли
4. ключевые и вторичные страницы `NauDoc`
5. `middleware` и согласованность bridge-ссылок

## Digital Signature Audit

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./audit_digital_signature.py
```

Скрипт проверяет:

1. что add-on `DigitalSignature` активирован в портале
2. что админская форма `manage_signature_form` открывается
3. что у пользователя доступен выбор сертификата в `personalize_form`
4. что у `HTMLDocument` есть вкладка `Подписи`
5. что форма `document_signatures_form` отдается корректно

## Журнал Sync-Ошибок

В `Bridge` теперь есть рабочий журнал sync-ошибок:

1. страница: `https://localhost:18443/bridge/`
2. раздел: `Журнал ошибок синхронизации`
3. кнопка `Повторить` запускает реальный внутренний sync-job
4. кнопка `Закрыть` переводит запись в `resolved` после ручной проверки

Источник повторного запуска защищен и не публикуется наружу через gateway:

1. публичный `https://localhost:18443/run_sync_job.php` возвращает `404`
2. внутренний endpoint используется только `Bridge`

## LDAP-first groundwork

В `Bridge` теперь есть два новых GUI-слоя под единый каталог пользователей:

1. `Источники идентификации`
2. `Hospital-роли`

Что это дает уже сейчас:

1. админ видит, какие каталоги участвуют в платформе:
   - локальный `Rukovoditel`
   - `NauDoc`
   - будущий `LDAP/AD`
2. админ может через GUI настраивать:
   - provider type
   - sync mode
   - host / port / DN
   - атрибуты `login / email / department / role`
   - bind DN и имя env-ключа для секрета
3. hospital-роли отделены от технических ролей источников:
   - `ИТ-администратор`
   - `Заведующий отделением`
   - `Врач`
   - `Регистратура`
   - `Канцелярия`

Важно:

1. пароль LDAP не хранится в `Bridge`
2. секреты остаются в корневом `.env`
3. это groundwork для `LDAP/SSO`, а не уже готовый SSO

## GUI-Маппинг Статусов

В `Bridge` теперь есть GUI-настройка маппинга статусов:

1. страница: `https://localhost:18443/bridge/`
2. раздел: `Маппинг статусов`
3. администратор может:
   - добавлять правило
   - менять тип совпадения `contains / exact / prefix`
   - задавать статус заявки
   - задавать статус документа
   - задавать статус интеграции
   - включать и выключать правило
   - менять порядок применения

Эти правила используются в `pull_bridge_updates.php`, то есть влияют на реальную обратную синхронизацию статусов в `Rukovoditel`.

## GUI-Маппинг Полей

В `Bridge` теперь есть GUI-настройка маппинга полей:

1. страница: `https://localhost:18443/bridge/`
2. раздел: `Маппинг полей`
3. администратор может:
   - добавлять правило
   - менять источник и назначение
   - задавать направление `push / pull / bidirectional`
   - отмечать обязательные поля
   - включать и выключать правило

Сейчас эти правила уже используются:

1. при записи metadata из `Rukovoditel` в `Bridge`
2. при формировании честной проекции полей для `NauDoc` внутри `Bridge`
3. при прямом `Bridge -> NauDoc` write-back для `document_cards`
4. при обратной передаче конкретного `NauDoc` URL в `service_requests` и `projects`

Важно:

1. на текущем этапе это уже реальная GUI-настройка полей
2. `Bridge` уже не только хранит projection, но и создает/обновляет реальные объекты `NauDoc`
3. write-back сейчас доведен для маршрута:
   - `document_cards -> NauDoc object`
   - `service_requests/projects -> reuse конкретного NauDoc URL карточки`
4. следующим шагом остается доведение business-логики write-back под финальные hospital-маршруты

## Ручная Перевязка Связей

В `Bridge` теперь есть рабочая `manual relink`-механика:

1. страница: `https://localhost:18443/bridge/`
2. раздел: `Текущие связи`
3. действие: `Ручная перевязка`

Администратор может вручную поменять:

1. внешнюю сущность
2. внешний ID
3. название записи
4. комментарий
5. metadata JSON

При перевязке обновляется не только сама связь, но и привязанные записи `sync_failures`.

## Каталог Пользователей

В `Bridge` теперь есть groundwork для единого каталога пользователей:

1. страница: `https://localhost:18443/bridge/`
2. раздел: `Каталог пользователей`
3. источник данных:
   - `sync_naudoc_profiles.sh`
4. уже доступны:
   - matched/unmatched профили
   - `needs_review` профили
   - ссылка на профиль в `NauDoc`
   - роль и email связанного профиля
   - подсказка по вероятному сопоставлению
   - кнопка `Принять подсказку`
   - ручное сопоставление профиля в GUI

Это еще не `SSO`, но уже рабочая база для дальнейшего перехода к единому каталогу пользователей.

## Document Cards Sync

Для production-контура отдельные карточки документов синхронизируются не только косвенно через заявки и проекты, но и напрямую:

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash sync_document_cards.sh --force-all
```

Что это дает:
1. вручную созданные карточки тоже получают конкретный объект в `NauDoc`
2. ссылка `Ссылка на NauDoc` доезжает обратно в `Rukovoditel`
3. `Bridge` хранит конкретную связь `document_cards -> NauDoc`, а не только общую ссылку на `/docs`

## ONLYOFFICE Audit

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./audit_onlyoffice_integration.py
```

Скрипт проверяет:

1. что пилотный `docx` существует в `Карточки документов`
2. что editor page открывается в `desktop` и `mobile` режиме
3. что `downloadUrl` и `callbackUrl` строятся на внутренний host `http://rukovoditel/`
4. что `ONLYOFFICE Document Server` получает реальный `docx`
5. что callback с валидным JWT проходит успешно
6. что `download_token` очищается и перевыпускается корректно

## Restore NauDoc Addons

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./restore_naudoc_addons_from_pyc.py
```

Скрипт восстанавливает legacy add-ons `NauDoc` из `.pyc` в `.py`.
Нужен для ситуаций, когда в поставке нет исходников add-ons, а runtime не может загрузить старые compiled-файлы напрямую.

## Важно

1. `restore_all.sh` меняет рабочие данные
2. перед восстановлением лучше сделать свежий backup
3. для локального стенда gateway работает с self-signed сертификатом
4. для production переменные и секреты нужно брать из `.env`, шаблон лежит в [`.env.example`](/home/lebedeffson/Code/Документооборот/.env.example)
5. первый успешный локальный restore drill зафиксирован в [RESTORE_DRILL_REPORT.md](/home/lebedeffson/Code/Документооборот/docs/reference/RESTORE_DRILL_REPORT.md)
