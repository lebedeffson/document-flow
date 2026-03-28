# Hospital Release Checklist

Дата: `2026-03-28`

## 1. Зафиксированная модель первой production-волны

В первую боевую волну входит:

1. `Rukovoditel` как основной рабочий кабинет
2. `ONLYOFFICE Docs` как встроенный редактор из карточки документа
3. `NauDoc` как служебный официальный документный контур
4. `Bridge` как внутренний admin/integration слой
5. `ONLYOFFICE DocSpace` как ограниченный внешний collaboration-контур
6. `ONLYOFFICE Workspace` как ограниченный корпоративный сервисный слой

Ограничение первой волны:

1. `DocSpace` и `Workspace` не заменяют основной рабочий кабинет
2. бизнес-процессы, роли, заявки и карточки документов остаются в `Rukovoditel`
3. `Workspace` должен закрывать только те функции, которых реально нет в `Rukovoditel`

## 2. Release Gate перед hospital production

До первого реального релиза должны быть закрыты все пункты ниже.

### 2.1 Infrastructure baseline

1. На сервере больницы подготовлен боевой `.env`
2. Зафиксированы production-domain, public URLs и TLS
3. Лишние прямые порты наружу закрыты
4. Контур поднимается из hospital `.env` без ручных временных правок

### 2.2 Backup and recovery

1. Включен `backup` timer
2. Есть свежий backup всех трех контуров
3. Пройден `restore drill` на staging или production-like сервере
4. У ИТ-службы есть понятный runbook восстановления

### 2.3 Identity and access

1. Утверждена финальная hospital role matrix
2. Назначены реальные пользователи по ролям
3. Подтвержден каталог пользователей:
   `LDAP/AD` или переходная согласованная схема
4. Для каждой роли подтвержден свой UI без лишней demo-семантики

### 2.4 Document routes

1. Выбраны 2-3 реальных hospital-маршрута для первой волны
2. Для них зафиксированы:
   тип документа, статусы, владельцы этапов, правила регистрации
3. Подтверждено, где черновик живет в `Rukovoditel/ONLYOFFICE`, а где официальный статус живет в `NauDoc`

### 2.5 Office ecosystem

1. `DocSpace` поднят и открывается по production/staging URL
2. `Workspace` поднят и открывается по production/staging URL
3. Для карточек или проектов зафиксированы понятные ссылки/точки входа
4. Подтверждено, что `DocSpace/Workspace` не дублируют основной сценарий работы в `Rukovoditel`

### 2.6 Staging gate

1. Есть отдельный `staging`, не делящий production `.env` и порты
2. На staging проходят:
   `prod_readiness_audit.py`, `check_stack.sh`, `smoke_test_stack.sh`, `run_full_verification.sh`, `restore_drill.sh`
3. Monitoring snapshot не показывает падения core-сервисов

### 2.7 Pilot and acceptance

1. Выбрано одно подразделение для пилота
2. Загружены реальные пользователи пилота
3. Проведено короткое обучение
4. Хотя бы один маршрут проходит путь:
   черновик -> согласование -> официальный документ
5. Ошибки синхронизации видны и обрабатываются штатно

## 3. Что можно сделать прямо сейчас в репозитории

### 3.1 Подготовить candidate env

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/generate_prod_env.sh
bash ops/generate_staging_env.sh
```

### 3.2 Проверить candidate env

```bash
cd /home/lebedeffson/Code/Документооборот
DOCFLOW_ENV_FILE=/home/lebedeffson/Code/Документооборот/.env.generated.hospital python3 ops/prod_readiness_audit.py
```

### 3.3 Проверить живой baseline

```bash
cd /home/lebedeffson/Code/Документооборот
python3 ops/prod_readiness_audit.py
python3 ops/monitoring_snapshot.py
python3 ops/audit_database_integrity.py
```

## 4. Что обязательно требуется от больницы

Без этого выпуск нельзя считать завершенным:

1. реальный внутренний домен, IP и TLS-схема
2. реальные LDAP/AD-параметры или утвержденная переходная identity-модель
3. список пользователей первой волны
4. список ролей и подразделений первой волны
5. выбор пилотного отделения
6. выбор 2-3 реальных document routes для запуска
7. решение, для каких конкретно сценариев первой волны используются `DocSpace` и `Workspace`

## 5. Момент перехода к release-candidate

В `release-candidate` переводим сборку только когда одновременно:

1. operating model заморожена
2. hospital `.env` проверен
3. restore drill на staging подтвержден
4. роли и каталог пользователей согласованы
5. `DocSpace` и `Workspace` подняты в согласованном scope первой волны
6. пилот на одном подразделении пройден
7. список post-pilot замечаний разобран и отфильтрован на blockers / non-blockers
