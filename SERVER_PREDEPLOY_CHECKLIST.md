# Server Predeploy Checklist

Дата: `2026-03-24`

## 1. Короткий статус

Текущее состояние платформы:

1. Функционально контур работает
2. Автоматический аудит проходит
3. На тестовый сервер / пилотный контур заливать уже можно
4. На полноценный боевой production без дополнительной обвязки пока рано

Оценка:

1. Тестовый сервер: `готово условно`
2. Пилот: `почти готово`
3. Боевой production: `не готово`

---

## 2. Что уже готово

### Функциональный контур

- `DONE` `Rukovoditel` работает
- `DONE` `NauDoc` работает
- `DONE` `middleware` работает
- `DONE` `gateway` работает
- `DONE` `request -> doc card -> bridge -> pull`
- `DONE` `project -> doc card -> bridge -> pull`
- `DONE` роли и ролевые меню работают
- `DONE` полный аудит дает `failures = 0`
- `DONE` ранее broken add-ons `NauDoc` восстановлены в рабочее состояние

### Технический контур

- `DONE` `HTTP -> HTTPS redirect`
- `DONE` единый вход через gateway
- `DONE` restart policy у контейнеров: `unless-stopped`
- `DONE` есть backup-скрипт
- `DONE` есть restore-скрипт
- `DONE` есть smoke-test
- `DONE` есть full contour audit

### Эксплуатационные артефакты

- `DONE` [ops/check_stack.sh](/home/lebedeffson/Code/Документооборот/ops/check_stack.sh)
- `DONE` [ops/smoke_test_stack.sh](/home/lebedeffson/Code/Документооборот/ops/smoke_test_stack.sh)
- `DONE` [ops/full_contour_audit.py](/home/lebedeffson/Code/Документооборот/ops/full_contour_audit.py)
- `DONE` [ops/backup_all.sh](/home/lebedeffson/Code/Документооборот/ops/backup_all.sh)
- `DONE` [ops/restore_all.sh](/home/lebedeffson/Code/Документооборот/ops/restore_all.sh)
- `DONE` [ops/restore_naudoc_addons_from_pyc.py](/home/lebedeffson/Code/Документооборот/ops/restore_naudoc_addons_from_pyc.py)

---

## 3. Что не готово к нормальному серверу

### Конфигурация и секреты

- `TODO` убрать тестовые логины и пароли
- `TODO` вынести пароли в `.env` или secrets
- `TODO` сделать отдельный `prod`-конфиг
- `TODO` убрать `localhost` и тестовые URL из серверной конфигурации

Сейчас в тестовом виде используются:

1. `admin / admin`
2. `admin / admin123`
3. `rukovoditel / rukovoditel`
4. `root_rukovoditel`

### Сеть и сертификаты

- `PARTIAL` `HTTPS` есть, но сертификат `self-signed`
- `TODO` поставить реальный домен
- `TODO` поставить реальный TLS-сертификат
- `TODO` наружу оставить только gateway `80/443`
- `TODO` закрыть прямой внешний доступ к `18080/18081/18082`

### Backup и восстановление

- `DONE` backup-скрипты существуют
- `PARTIAL` restore-сценарий существует, но нужен регулярный restore drill
- `TODO` автоматизировать backup по расписанию
- `TODO` настроить ротацию backup
- `TODO` выносить backup вне сервера / VM

### Наблюдаемость

- `PARTIAL` есть health-check и audit
- `TODO` добавить централизованные логи
- `TODO` добавить мониторинг ошибок sync worker
- `TODO` добавить алерты по отказам и диску

### Серверная организация

- `TODO` разделить `staging` и `production`
- `TODO` оформить единый `prod-runbook`
- `TODO` оформить обновление без ручной импровизации

### Бизнес-риски перед продом

- `PARTIAL` основной контур документов и интеграции рабочий
- `TODO` отдельно глубоко прогнать `DigitalSignature / ЭЦП`
- `TODO` отдельно прогнать реальные приемочные кейсы пользователей
- `TODO` убрать или ограничить тестовых пользователей перед боем

---

## 4. Что обязательно сделать перед тестовым сервером

Это минимальный пакет, без которого лучше не переносить даже тестовый сервер.

- `TODO` выбрать боевой URL или временный домен
- `TODO` собрать `.env` для сервера
- `TODO` сменить все тестовые пароли
- `TODO` закрыть прямые тестовые порты наружу
- `TODO` сделать первый полный backup перед переносом
- `TODO` задокументировать команды запуска и восстановления

Решение:

1. После этих пунктов можно поднимать серверный тестовый контур

---

## 5. Что обязательно сделать перед пилотом

- `TODO` реальный сертификат
- `TODO` автоматические backup по расписанию
- `TODO` restore drill
- `TODO` SMTP и уведомления
- `TODO` реальные пользователи и роли подразделений
- `TODO` приемочные сценарии по документам, заявкам и проектам
- `TODO` финальная проверка маршрутов документов

Решение:

1. После этих пунктов можно пускать пилотную группу

---

## 6. Что обязательно сделать перед production

- `TODO` staging отдельно от production
- `TODO` централизованные логи
- `TODO` мониторинг и алерты
- `TODO` регламент сопровождения
- `TODO` offsite backup
- `TODO` проверка `ЭЦП`
- `TODO` security hardening
- `TODO` процедура обновления и отката

Решение:

1. Только после этого можно считать платформу production-ready

---

## 7. Текущий Go / No-Go

### На тестовый сервер

Решение: `GO`, но после минимального пакета конфигурации и секретов

### На пилот

Решение: `GO LATER`, сначала закрыть backup, TLS, SMTP, реальные учетные данные и приемку

### На production

Решение: `NO-GO`, пока не закрыты безопасность, эксплуатация и прод-обвязка

---

## 8. Что я рекомендую делать следующим пакетом

Порядок без расползания:

1. Сделать `prod env + домен + реальные пароли + закрыть прямые порты`
2. Собрать `server deploy` пакет
3. Настроить `backup schedule + restore drill`
4. Прогнать `ЭЦП`
5. Подготовить staging / pilot

---

## 9. Ближайший рабочий backlog

### Пакет A. Server Config

- `TODO` `.env.production`
- `TODO` `docker-compose.production.yml`
- `TODO` реальные URL и имена контейнеров
- `TODO` убрать test-порты наружу

### Пакет B. Security

- `TODO` сменить все пароли
- `TODO` скрыть внутренние сервисы
- `TODO` подключить реальный сертификат

### Пакет C. Operations

- `TODO` cron/systemd timer для backup
- `TODO` логирование и журнал ошибок
- `TODO` инструкция запуска / остановки / отката

### Пакет D. Acceptance

- `TODO` приемка по реальным подразделениям
- `TODO` deep test `ЭЦП`
- `TODO` удаление тестовых аккаунтов перед боем

---

## 10. Команды контроля перед заливкой

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./check_stack.sh
./smoke_test_stack.sh
./full_contour_audit.py
```

Ожидаемое состояние:

1. `check_stack` -> без ошибок
2. `smoke_test_stack` -> без ошибок
3. `full_contour_audit.py` -> `failures = 0`
