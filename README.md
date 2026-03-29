# Платформа документооборота: старт и проверка

Дата актуальности: `2026-03-27`

## 1. С чего начинать

Главный адрес платформы:

- `https://localhost:18443/`

Официальный документный контур:

- `https://localhost:18443/docs/`

Служебный интеграционный контур:

- `https://localhost:18443/bridge/`

Использовать нужно только эти адреса.

Не использовать:

- `https://localhost/docs/`
- прямые внутренние порты `18080`, `18081`, `18082`, `18083`
- прямой служебный URL `ONLYOFFICE`

---

## 2. Кто как входит

### Администратор

- логин: `admin`
- пароль: из `DOCFLOW_ADMIN_PASSWORD`

Это полный контур сопровождения:

- настройки
- пользователи и роли
- резервные копии
- логи
- интеграции
- все рабочие модули

### Простой пользователь

- логин: рабочая учетная запись сотрудника
- пароль: из `DOCFLOW_ROLE_DEFAULT_PASSWORD`

Это чистый пользовательский режим:

- заявки
- задачи
- проекты
- карточки документов
- база документов
- МТЗ
- переход в `NauDoc`
- работа с документом через `ONLYOFFICE`

### NauDoc

- логин: `admin`
- пароль не фиксируется в документации
- актуальное значение хранится в корневом `.env` в переменной `NAUDOC_PASSWORD`

Это отдельная авторизация для официального документного контура.

### Каталог пользователей и роли

В `Bridge` уже есть рабочая база для единого каталога пользователей:

1. профили из `NauDoc` подтягиваются через `sync_naudoc_profiles.sh`
2. exact-match по `username` связывает профиль автоматически
3. если username не совпадает, `Bridge` может показать подсказку по отображаемому имени
4. администратор может принять подсказку прямо в GUI
5. в каталоге уже видно:
   - роль связанного профиля
   - email
   - статус `matched / manual_match / needs_review / unmatched`

Это еще не `LDAP/SSO`, но уже рабочий переходный слой к hospital-production модели доступа.

---

## 3. Что тестировать под админом

Войти:

- `https://localhost:18443/`
- `admin / пароль из DOCFLOW_ADMIN_PASSWORD`

Проверить:

1. Главная администратора
   - заголовок `Центр управления платформой`
   - блок состояния контура
   - системные разделы
   - рабочий контур
2. Пользователи и роли
3. Настройки приложения
4. Сущности приложения
5. Группы доступа
6. Резервные копии
7. Логи
8. Интеграции:
   - `NauDoc`
   - `Bridge`
   - встроенный редактор `ONLYOFFICE Docs`
9. Рабочие модули:
   - Заявки
   - Проекты
   - Документы
   - База документов
   - МТЗ

Админский режим нужен для проверки полной платформы и сопровождения.

---

## 4. Что тестировать под пользователем

Войти:

- `https://localhost:18443/`
- рабочая учетная запись сотрудника / пароль из `DOCFLOW_ROLE_DEFAULT_PASSWORD`

Проверить:

1. Главная пользователя
   - заголовок `Рабочий кабинет`
   - нет перегруженной админки
   - только рабочие разделы
2. Раздел `Заявки на обслуживание`
3. Раздел `Поручения и задачи`
4. Раздел `Проекты и инициативы`
5. Раздел `Карточки документов`
6. Раздел `База документов`
7. Раздел `Заявки на МТЗ`
8. Переход в `NauDoc`
9. Открытие документа в редакторе

Пользовательский режим нужен для проверки того, что платформа понятна без технического шума.

Краткая матрица пользовательских возможностей:

- [USER_CAPABILITY_MATRIX.md](/home/lebedeffson/Code/Документооборот/docs/reference/USER_CAPABILITY_MATRIX.md)
- [PILOT_USER_LIST_TEMPLATE.md](/home/lebedeffson/Code/Документооборот/docs/reference/PILOT_USER_LIST_TEMPLATE.md)
- [pilot_users_template.csv](/home/lebedeffson/Code/Документооборот/docs/reference/pilot_users_template.csv)

---

## 5. Как правильно проверять документный сценарий

Правильный путь такой:

1. Войти в платформу
2. Открыть `Карточки документов`
3. Открыть документ
4. Нажать `Открыть документ в редакторе`
5. При необходимости открыть `Открыть в NauDoc`

Это основной сквозной сценарий платформы.

---

## 6. Где находится ONLYOFFICE

`ONLYOFFICE Docs` встроен в платформу, но открывать его нужно только из карточки документа.

Правильный путь:

1. войти в платформу
2. открыть `Карточки документов`
3. открыть карточку документа
4. нажать `Открыть документ в редакторе`

Для контрольной проверки удобно использовать рабочий документ в разделе `Карточки документов`.

Самый простой контрольный сценарий:

1. открыть `Рабочий документ отделения: Иван Иванов`
2. нажать `Открыть документ в редакторе`
3. внести любую правку
4. убедиться, что карточка и ссылка `NauDoc` остались доступными

Дополнительные простые hospital-сценарии:

1. `Направление пациента: Иван Иванов`
2. `Медицинская запись отделения: Иван Иванов`
3. `Внутренний приказ отделения: график обходов`

---

## 7. Что реально встроено

Уже работает в текущем стенде:

1. `Rukovoditel` как рабочий кабинет
2. `NauDoc` как официальный документный контур
3. `ONLYOFFICE Docs` как встроенный веб-редактор
4. `Bridge` как интеграционный слой

`DocSpace` и `Workspace` теперь входят в scope первой production-волны, но ограниченно.
При этом в текущем стенде они еще не подняты как живые отдельные сервисы, поэтому до релиза их нужно развернуть и проверить отдельно.

Зафиксированный минимальный scope первой волны такой:

1. `DocSpace`:
   - `Collaboration rooms`
   - `Public rooms`
   - при необходимости `Form filling rooms`
2. `Workspace`:
   - `Calendar`
   - опционально `Community` как новости или база знаний
   - по умолчанию первая волна держит lean-mode: `Calendar` включен всегда, `Community` включается отдельным env-флагом

Что не берем в первую волну:

1. `Workspace Mail`
2. `Workspace CRM`
3. `Workspace Projects`
4. `Workspace Documents`

Это сделано специально, чтобы не дублировать `Rukovoditel` и не перегружать внедрение.

Для закрытой локальной сети и выездной выкладки теперь есть отдельный короткий go-live checklist:

- [CLOSED_LAN_GO_LIVE_CHECKLIST.md](/home/lebedeffson/Code/Документооборот/docs/reference/CLOSED_LAN_GO_LIVE_CHECKLIST.md)

---

## 8. Где нужен Bridge

`Bridge` нужен не обычному пользователю, а для:

1. контроля связей между контурами
2. проверки синхронизации
3. анализа проблемных связей
4. админской диагностики

Открывать его стоит в первую очередь под `admin`.

---

## 9. Как быстро привести стенд в порядок перед тестом

Обновить рабочий baseline:

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash prepare_hospital_baseline.sh
```

Прогнать полный verify:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/run_full_verification.sh
```

---

## 10. Как перенести платформу на сервер с флешки

Если нужно один раз собрать платформу на рабочей машине и потом перенести ее на Linux-сервер без сложной установки из интернета, используйте offline bundle:

Проверка готовности bundle:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/create_portable_bundle.sh --verify-only --with-local-ldap
```

Полная сборка bundle:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/create_portable_bundle.sh --with-local-ldap
```

Установка на сервере:

```bash
cd /path/to/bundle
bash install_from_bundle.sh /opt/docflow
```

Полный runbook:

- [OFFLINE_INSTALL_RUNBOOK.md](/home/lebedeffson/Code/Документооборот/docs/reference/OFFLINE_INSTALL_RUNBOOK.md)

Если нужно не только установить стенд, но и подготовить пакет для пилота на одном подразделении:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/create_pilot_package.sh
```

Опорный документ:

- [PILOT_RUNBOOK.md](/home/lebedeffson/Code/Документооборот/docs/reference/PILOT_RUNBOOK.md)

Проверить production-readiness базового контура:

```bash
cd /home/lebedeffson/Code/Документооборот
python3 ops/prod_readiness_audit.py
```

Шаблон production-переменных:

```bash
cp .env.example .env
```

Синхронизировать профили из `NauDoc`:

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash sync_naudoc_profiles.sh
```

После этого в `Bridge` обновится раздел `Каталог пользователей`.

Обновить GUI-маппинг полей и проекцию в `NauDoc`:

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash sync_document_cards.sh --force-all
bash sync_service_requests.sh --force-all
bash sync_project_documents.sh --force-all
```

После этого в связях `Bridge` появится актуальная `Проекция в NauDoc` для карточек документов, заявок и проектов, включая карточки, созданные вручную.

---

## 10. Какие файлы сейчас основные

Рабочие документы в корне проекта:

- [README.md](/home/lebedeffson/Code/Документооборот/README.md)
- [USER_QUICKSTART_GUIDE.md](/home/lebedeffson/Code/Документооборот/USER_QUICKSTART_GUIDE.md)
- [CUSTOMER_PRESENTATION_SCRIPT.md](/home/lebedeffson/Code/Документооборот/CUSTOMER_PRESENTATION_SCRIPT.md)
- [HOSPITAL_PRODUCTION_ROADMAP.md](/home/lebedeffson/Code/Документооборот/HOSPITAL_PRODUCTION_ROADMAP.md)
- [UNIFIED_PROD_PLATFORM_PLAN.md](/home/lebedeffson/Code/Документооборот/UNIFIED_PROD_PLATFORM_PLAN.md)

Если нужна именно production-картина по больничному внедрению, основной опорный документ сейчас:

- [HOSPITAL_PRODUCTION_ROADMAP.md](/home/lebedeffson/Code/Документооборот/HOSPITAL_PRODUCTION_ROADMAP.md)
- [HOSPITAL_NEXT_STEPS_PLAN.md](/home/lebedeffson/Code/Документооборот/docs/reference/HOSPITAL_NEXT_STEPS_PLAN.md)
- [HOSPITAL_TARGET_OPERATING_MODEL.md](/home/lebedeffson/Code/Документооборот/docs/reference/HOSPITAL_TARGET_OPERATING_MODEL.md)
- [HOSPITAL_RELEASE_CHECKLIST.md](/home/lebedeffson/Code/Документооборот/docs/reference/HOSPITAL_RELEASE_CHECKLIST.md)
- [UNIFIED_PROD_PLATFORM_PLAN.md](/home/lebedeffson/Code/Документооборот/UNIFIED_PROD_PLATFORM_PLAN.md)
- [REFERENCE_DATA_CATALOG.md](/home/lebedeffson/Code/Документооборот/REFERENCE_DATA_CATALOG.md)

Технические отчеты и справочные матрицы перенесены в:

- `docs/reference/`

Архивные и промежуточные планы перенесены в:

- `docs/archive/`

Старые дистрибутивы, PDF-мануалы и legacy-материалы вынесены в:

- `docs/legacy/`
