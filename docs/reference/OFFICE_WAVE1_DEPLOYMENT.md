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

## 2. Рекомендуемая production-топология

Для первой боевой волны лучше считать `DocSpace` и `Workspace` отдельными office-hosts, а не пытаться запихнуть их в тот же хост, где уже живут:

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
  --require-live-targets
```

Это делает:

1. записывает target URL в `.env`
2. включает жесткий production-режим для office-wave1
3. обновляет baseline-ссылки в проектах, заявках, документах, базе документов и МТЗ

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
