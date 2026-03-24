# Ops

Минимальный набор эксплуатационных скриптов для production-lite контура.

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

## Restore

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./restore_all.sh /home/lebedeffson/Code/Документооборот/backups/20260324-120000
```

## Health checks

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./check_stack.sh
```

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
