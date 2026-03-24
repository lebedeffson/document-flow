# Rukovoditel Test Stand

This directory contains the test deployment of `Rukovoditel 3.6.4` running next to the legacy `NauDoc` stack and the new middleware bridge.

## Services

- `NauDoc`: `http://localhost:18080/docs`
- `Rukovoditel`: `http://localhost:18081/`
- `Middleware`: `http://localhost:18082/`
- `ONLYOFFICE Docs`: `http://localhost:18083/`
- `MariaDB`: internal only, service name `rukovoditel_db`
- `Sync Worker`: background sync loop inside `rukovoditel_sync_worker_test`

## Start

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
docker compose up -d --build
```

## Installed values

- DB Host: `rukovoditel_db`
- DB Port: `3306`
- DB Name: `rukovoditel`
- DB User: `rukovoditel`
- DB Password: `rukovoditel`
- Admin login: `admin`
- Admin password: `admin123`

## Notes

- `Rukovoditel` is already installed.
- `NauDoc` runs from `/home/lebedeffson/Code/Документооборот/naudoc_project`.
- The bridge stores links between `Rukovoditel` records and `NauDoc` document URLs in its own SQLite database.

## Apply process model

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash apply_process_model.sh
```

This provisioning script creates and updates:

- entity groups for navigation
- projects, tasks, service requests, document cards, document base, and MTO request entities
- tabs, fields, statuses, and access schemas for the test stand
- common dashboard reports for employees and managers
- document integration status fields for projects and service requests
- pilot `ONLYOFFICE` draft field in `Карточки документов`

## ONLYOFFICE pilot

Wave 1 now targets the `Карточки документов` entity.

Public editor API URL:

- `https://localhost:18443/office/web-apps/apps/api/documents/api.js`

Internal editor service:

- `http://localhost:18083/`

The pilot field is created as:

- `Рабочий черновик`

JWT secret used by the test stand:

- `onlyoffice_dev_secret`

Repeatable pilot setup:

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash seed_onlyoffice_pilot.sh
```

This script:

- creates or reuses a pilot `docx`
- attaches it to `Карточки документов` item `#1`
- fixes file ownership for Apache inside the container
- keeps the pilot flow reproducible after restarts

## Sync service requests to document cards

The first working automation scenario is now available:

- create or find a service request in `Rukovoditel`
- create a linked document card automatically
- publish bridge records to the middleware
- prepare the reverse sync path back into `Rukovoditel`
- show status of linked documents directly in request and project cards

The second working automation scenario is also available:

- create or find a project in `Rukovoditel`
- create a linked document card for the project
- publish project bridge records to the middleware
- pull finalized `NauDoc` data back into the project card

Run:

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash sync_service_requests.sh
```

For a reproducible end-to-end test with demo data:

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash sync_service_requests.sh --seed-demo
```

The sync script lives in:

- `dist/scripts/sync_service_requests.php`
- `sync_service_requests.sh`

## Sync projects to document cards

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash sync_project_documents.sh --seed-demo
```

Optional filters:

- `--project-id=1`
- `--force-all`

The project sync script lives in:

- `dist/scripts/sync_project_documents.php`
- `sync_project_documents.sh`

## Pull bridge updates back into Rukovoditel

When a real `NauDoc` URL and status appear in the bridge, they can be written back into the request and document card:

```bash
cd /home/lebedeffson/Code/Документооборот/rukovoditel-test
bash pull_bridge_updates.sh --only-linked
```

Optional filters:

- `--request-id=1`
- `--doc-card-id=1`

The pull script lives in:

- `dist/scripts/pull_bridge_updates.php`
- `pull_bridge_updates.sh`

## Background sync worker

The test stand now includes a background worker that periodically runs:

1. `sync_service_requests.php`
2. `sync_project_documents.php`
3. `pull_bridge_updates.php`

Container:

- `rukovoditel_sync_worker_test`

Logs:

```bash
docker logs -f rukovoditel_sync_worker_test
```

Visible reports added for managers:

- `Заявки без финального документа`
- `Проекты с риском по документам`

## First bridge scenario

1. Create tasks, projects, or service requests in `Rukovoditel`.
2. Keep documents, approvals, and archive in `NauDoc`.
3. Use the sync scripts to create linked document cards for requests and projects.
4. Store bridge records and sync notes in the middleware at `http://localhost:18082/`.
5. Set the final `NauDoc` URL and bridge status in the middleware UI or through `/links/upsert`.
6. Run `pull_bridge_updates.sh --only-linked` to update `Rukovoditel`.
7. Extend this layer later with direct write-back into `NauDoc`.
