# Office Wave 1 Deployment

Дата: `2026-03-28`

## 1. Что считается полным production-состоянием

Для финального hospital production недостаточно `shell-only` режима.

Полный production-state для office-ecosystem означает:

1. `DocSpace` поднят как отдельный live-сервис
2. `Workspace` поднят как отдельный live-сервис
3. в `.env` заданы реальные `DOCSPACE_TARGET_URL` и `WORKSPACE_TARGET_URL`
4. включен `DOCFLOW_OFFICE_WAVE1_REQUIRE_LIVE_TARGETS=1`
5. `prod_readiness_audit.py` проходит без office-warning
6. `Workspace` в первой волне зафиксирован в lean-mode: `Calendar` всегда доступен, `Community` включается только отдельным флагом `DOCFLOW_WORKSPACE_WAVE1_ENABLE_COMMUNITY=1`
7. при необходимости можно задать и отдельные deep-link URL:
   - `DOCSPACE_COLLABORATION_ROOM_TARGET_URL`
   - `DOCSPACE_PUBLIC_ROOM_TARGET_URL`
   - `DOCSPACE_FORM_FILLING_ROOM_TARGET_URL`
   - `WORKSPACE_CALENDAR_TARGET_URL`
   - `WORKSPACE_COMMUNITY_TARGET_URL`

Зафиксированный минимальный scope первой волны:

1. `DocSpace`:
   - `Collaboration rooms`
   - `Public rooms`
   - при необходимости `Form filling rooms`
2. `Workspace`:
   - `Calendar`
   - опционально `Community`

Что не включаем в первую волну:

1. `Workspace Mail`
2. `Workspace CRM`
3. `Workspace Projects`
4. `Workspace Documents`

## 2. Рекомендуемая production-топология

Для первой боевой волны есть два допустимых production-варианта:

1. отдельные office-hosts
2. тот же server/IP, но через `same-host reverse proxy` под тем же gateway

Отдельные office-hosts проще масштабировать, а same-host схема удобнее для закрытой локальной сети: один IP, один сертификат, один внешний адрес для пользователей.

Если идти по same-host схеме, пользователи заходят так:

1. `https://<server-ip>/` -> основной контур
2. `https://<server-ip>/docspace/` -> live `DocSpace` через gateway reverse proxy
3. `https://<server-ip>/workspace/` -> live `Workspace` через gateway reverse proxy

В этом случае `DOCSPACE_TARGET_URL` и `WORKSPACE_TARGET_URL` можно задавать как внутренние target URL на том же сервере, например:

```env
DOCSPACE_TARGET_URL=http://host.docker.internal:19001/
WORKSPACE_TARGET_URL=http://host.docker.internal:19002/
DOCFLOW_OFFICE_WAVE1_REQUIRE_LIVE_TARGETS=1
```

Gateway будет держать единый внешний адрес, а live office-сервисы останутся внутренними.

### 2.1 Допустимый low-memory режим для `16 GB`

Для первого hospital-внедрения с малой нагрузкой допустим и упрощенный same-host вариант:

1. `DocFlow + ONLYOFFICE Docs + DocSpace + Workspace` живут на одном сервере
2. `DocSpace` работает в live-режиме под `/docspace/`
3. `Workspace` работает в live-режиме под `/workspace/`
4. после первичного bootstrap отключается `Workspace Elasticsearch`
5. в `Workspace` остаются рабочими логин, портал и `Calendar`
6. полнотекстовый поиск `Workspace` в этом профиле считается временно отключенным

Этот режим годится только для:

1. первой production-выкладки в больнице
2. малой нагрузки
3. небольшого числа пользователей и документов
4. сервера уровня `~16 GB RAM / 6+ GB swap`

Это не полноценный capacity-profile под длительную активную эксплуатацию, а безопасный стартовый режим до расширения памяти.

Если же инфраструктура позволяет, отдельные office-hosts по-прежнему остаются хорошим вариантом, особенно если не хочется держать весь office-layer на одной машине.

Для отдельной схемы лучше считать `DocSpace` и `Workspace` отдельными office-hosts, а не пытаться запихнуть их в тот же хост, где уже живут:

1. `gateway`
2. `Rukovoditel`
3. `MariaDB`
4. `NauDoc`
5. `Bridge`
6. `ONLYOFFICE Docs`

Рекомендуемая схема:

1. `docflow.hospital.local` -> основной контур платформы
2. `docspace.hospital.local` -> live `ONLYOFFICE DocSpace`
3. `workspace.hospital.local` -> live `ONLYOFFICE Workspace`

Причина простая:

1. `DocSpace` Community официально требует минимум `6 CPU / 12 GB RAM / 40 GB disk / 6 GB swap`
2. `Workspace` Community официально требует минимум `4 CPU / 8 GB RAM / 40 GB disk / 6 GB swap`
3. суммарно на одном host это уже `20 GB RAM` и `12 GB swap` только под office-layer

## 3. Проверка хоста под office-ecosystem

Перед развертыванием проверить хост:

```bash
cd /home/lebedeffson/Code/Документооборот
python3 ops/office_wave1_host_audit.py
```

Скрипт показывает:

1. готов ли хост под `Workspace`
2. готов ли хост под `DocSpace`
3. можно ли поднимать их вместе на одном сервере
4. можно ли идти в `low_memory_same_host_pilot`

## 4. Практический порядок для полного production

### 4.1 Поднять live `DocSpace`

На отдельном host/VM:

1. выделить домен `docspace.hospital.local`
2. поставить TLS
3. развернуть `ONLYOFFICE DocSpace` по официальной инструкции ONLYOFFICE
4. убедиться, что сервис открывается по `https://docspace.hospital.local/`

Базовая official-команда:

```bash
curl -O https://download.onlyoffice.com/docspace/docspace-install.sh
sudo bash docspace-install.sh docker
```

### 4.2 Поднять live `Workspace`

На отдельном host/VM:

1. выделить домен `workspace.hospital.local`
2. поставить TLS
3. развернуть `ONLYOFFICE Workspace` по официальной инструкции ONLYOFFICE
4. убедиться, что сервис открывается по `https://workspace.hospital.local/`
5. в первой волне включить только `Calendar`, а `Community` оставить опциональным легким дополнением
6. не включать `Mail/CRM/Projects/Documents`, чтобы не раздувать внедрение и не дублировать `Rukovoditel`

Базовая official-команда:

```bash
curl -O https://download.onlyoffice.com/install/workspace-install.sh
sudo bash workspace-install.sh -ims false
```

Если нужен и Mail Server, тогда official full-install выглядит так:

```bash
curl -O https://download.onlyoffice.com/install/workspace-install.sh
sudo bash workspace-install.sh -md "yourdomain.com"
```

### 4.3 Включить live-target в платформе

После этого в основном проекте:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/configure_office_wave1.sh \
  --docspace-target https://docspace.hospital.local/ \
  --workspace-target https://workspace.hospital.local/ \
  --workspace-calendar-only \
  --require-live-targets
```

Это делает:

1. записывает target URL в `.env`
2. включает жесткий production-режим для office-wave1
3. оставляет в `Workspace` только `Calendar`, если явно не включать `Community`
4. если отдельные module/room target URL не заданы, модульные кнопки все равно ведут в live frontdoor соответствующего сервиса
5. обновляет baseline-ссылки в проектах, заявках, документах, базе документов и МТЗ

Для same-host reverse proxy можно задавать внутренние URL/порты того же сервера вместо отдельных DNS-имен. Пользователь все равно будет работать только через основной адрес gateway.

Для этого варианта есть и единый cutover-сценарий:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/cutover_closed_lan_prod.sh --auto-host
```

Он по умолчанию включает:

1. `DOCSPACE_TARGET_URL=http://host.docker.internal:19001/`
2. `WORKSPACE_TARGET_URL=http://host.docker.internal:19002/`
3. `DOCFLOW_OFFICE_WAVE1_REQUIRE_LIVE_TARGETS=1`
4. `Workspace` в `Calendar`-only режиме

Если внутренние порты отличаются, их можно передать явно:

```bash
bash ops/cutover_closed_lan_prod.sh \
  --host 172.16.10.20 \
  --docspace-port 29001 \
  --workspace-port 29002
```

Для low-memory same-host развертывания на сервере около `16 GB` используйте:

```bash
cd /home/lebedeffson/Code/Документооборот
sudo bash ops/install_office_live_same_host.sh --auto-host --low-memory-profile
```

Этот сценарий:

1. ставит live `DocSpace`
2. ставит live `Workspace`
3. подтверждает живой вход в оба сервиса
4. отключает `Workspace Elasticsearch`
5. оставляет рабочими `Calendar` и базовый портал `Workspace`

Если `Community` все-таки нужен в первой волне:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/configure_office_wave1.sh \
  --docspace-target https://docspace.hospital.local/ \
  --workspace-target https://workspace.hospital.local/ \
  --workspace-with-community \
  --require-live-targets
```

### 4.4 Что проверять по факту

Для `DocSpace` достаточно подтвердить:

1. открывается `Collaboration room`
2. открывается `Public room`
3. при необходимости открывается `Form filling room`

Для `Workspace` достаточно подтвердить:

1. открывается `Calendar`
2. при необходимости открывается `Community`
3. пользователю не торчат `Mail/CRM/Projects/Documents` как обязательный сценарий первой волны

Для low-memory режима дополнительно подтвердить:

1. вход в `Workspace` проходит без `Elasticsearch`
2. `Calendar` открывается
3. известно и принято, что полнотекстовый поиск временно выключен

## 5. Финальный release gate

После включения live-target режима должны проходить:

```bash
cd /home/lebedeffson/Code/Документооборот
python3 ops/prod_readiness_audit.py
python3 ops/monitoring_snapshot.py
bash ops/check_stack.sh
python3 ops/audit_ecosystem_integration.py
python3 ops/full_contour_audit.py
```

## 6. Что сейчас допустимо как переходный этап

До появления живых `DocSpace/Workspace` допустим только staging/pilot режим:

1. `DOCSPACE_TARGET_URL=`
2. `WORKSPACE_TARGET_URL=`
3. `DOCFLOW_OFFICE_WAVE1_REQUIRE_LIVE_TARGETS=0`
4. оба сервиса работают как `shell_only`

Для настоящего final production этого недостаточно.

## 7. Official references

1. `DocSpace Community install script`: `https://helpcenter.onlyoffice.com/docspace/installation/docspace-community-install-script.aspx`
2. `Workspace Community install script`: `https://helpcenter.onlyoffice.com/workspace/installation/workspace-community-install-script.aspx`
3. `Workspace separate servers / docker`: `https://helpcenter.onlyoffice.com/workspace/installation/workspace-enterprise-install-separately-docker.aspx`
