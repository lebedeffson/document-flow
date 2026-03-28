# NauDoc + Rukovoditel Integration Stand

Current test stand built according to the target scheme:

`Rukovoditel <-> Middleware <-> NauDoc`

## URLs

- `Gateway HTTP`: `http://localhost:18090`
- `Gateway HTTPS`: `https://localhost:18443`
- `NauDoc`: `http://localhost:18080/docs`
- `Rukovoditel`: `http://localhost:18081/`
- `Middleware UI`: `http://localhost:18082/`
- `Middleware health`: `http://localhost:18082/health`
- `Middleware links API`: `http://localhost:18082/links`
- `ONLYOFFICE Docs`: `http://localhost:18083/`

Unified public entrypoints through the gateway:

- `Rukovoditel`: `https://localhost:18443/`
- `NauDoc`: `https://localhost:18443/docs/`
- `Middleware`: `https://localhost:18443/bridge/`
- `ONLYOFFICE Docs API`: `https://localhost:18443/office/web-apps/apps/api/documents/api.js`

## Credentials

### NauDoc

- login: `admin`
- password: `admin`

### Rukovoditel

- login: `admin`
- password: from `DOCFLOW_ADMIN_PASSWORD`

## Running containers

- `naudoc34_legacy`
- `rukovoditel_test`
- `rukovoditel_sync_worker_test`
- `rukovoditel_db_test`
- `naudoc_bridge_test`
- `naudoc_gateway_test`
- `onlyoffice_docs_test`

## What works now

- legacy `NauDoc` is available from the code directory
- `Rukovoditel` is installed and available on its own URL
- middleware can reach both systems and returns health status
- middleware stores links between `Rukovoditel` records and `NauDoc` document URLs, including pending links
- middleware allows manual update of existing links from the web UI
- `Rukovoditel` has common dashboard reports for employees and managers
- a sync script creates a document card from a service request and publishes bridge records
- a sync script creates a document card from a project and publishes bridge records
- a pull script writes finalized `NauDoc` URLs and bridge statuses back into `Rukovoditel`
- a background worker now runs sync cycles automatically
- requests and projects have a visible field `Статус документа / интеграции`
- `middleware` has counters, quick filters, and a journal of unfinished/problematic links
- `Rukovoditel` has reports `Заявки без финального документа` and `Проекты с риском по документам`
- a demo end-to-end record already exists in the stand
- `Rukovoditel` has a pilot ONLYOFFICE field `Рабочий черновик` in `Карточки документов`
- the ONLYOFFICE pilot now has a seeded `docx` in document card `#1`
- editor config is verified for both `desktop` and `mobile`
- internal server-to-server URLs are used for `downloadUrl` and `callbackUrl`
- callback flow with JWT has been checked end-to-end

## Start commands

### NauDoc

```bash
cd /home/lebedeffson/Code/Документооборот
docker compose --project-directory /home/lebedeffson/Code/Документооборот -p naudoccode -f docker-compose.legacy.yml up -d --build
```

### Rukovoditel

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
docker compose up -d --build
```

### Middleware

```bash
cd /home/lebedeffson/Code/Документооборот/middleware
docker compose up -d --build
```

### Gateway

```bash
cd /home/lebedeffson/Code/Документооборот/gateway
docker compose up -d --build
```

### Apply process model in Rukovoditel

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash apply_process_model.sh
```

### Run the first working sync scenario

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash sync_service_requests.sh --seed-demo
```

### Run the project sync scenario

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash sync_project_documents.sh --seed-demo
```

### Pull bridge updates back into Rukovoditel

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash pull_bridge_updates.sh --only-linked
```

### Run health checks

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./check_stack.sh
```

### Seed the ONLYOFFICE pilot

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
./seed_onlyoffice_document.sh
```

### Seed the ONLYOFFICE spreadsheet pilot

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
source /home/lebedeffson/Code/Документооборот/ops/lib/runtime_env.sh
docflow_load_env /home/lebedeffson/Code/Документооборот
docflow_export_runtime
ITEM_ID="$(docker exec "${RUKOVODITEL_DB_CONTAINER}" mariadb -N -s -u"${RUKOVODITEL_DB_USER}" -p"${RUKOVODITEL_DB_PASSWORD}" "${RUKOVODITEL_DB_NAME}" -e "select id from app_entity_25 where field_242='Таблица дежурств отделения: апрель 2026' order by id desc limit 1;" | tr -d '\r')"
./seed_onlyoffice_document.sh "${ITEM_ID}" duty-schedule-april-2026.xlsx "Дежурные врачи" "Старшая медсестра смены" "Контрольная таблица для проверки Excel-сценария в ONLYOFFICE."
```

### Audit the ONLYOFFICE flow

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./audit_onlyoffice_integration.py
```

### Export a LAN manual test packet

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/export_lan_manual_test_packet.sh
```

### Create backup

```bash
cd /home/lebedeffson/Code/Документооборот/ops
./backup_all.sh
```

## Nearest next steps

1. Add controlled creation of a real `NauDoc` URL from the integration layer, not only manual assignment.
2. Extend the new gateway and ops layer with scheduled backups and external DNS / real TLS.
3. Add direct callbacks or scheduler for automatic bridge pull without manual launch.
4. Show integration/document status more visibly in project and request lists.
