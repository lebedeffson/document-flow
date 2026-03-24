# NauDoc Bridge

Middleware between the legacy `NauDoc` stack and `Rukovoditel`.

## What it does now

- checks availability of both systems
- stores links between `Rukovoditel` records and `NauDoc` document URLs
- supports pending links before the final `NauDoc` URL is known
- exposes JSON API and a small web UI for manual linking and upsert scenarios
- allows manual update of existing links from the web UI
- supports write-back scenarios where `Rukovoditel` pulls finalized `NauDoc` URLs and statuses from the bridge
- shows summary counters and quick filters for operators
- includes a visual list of problematic or unfinished links

## URLs

- Public gateway UI: `https://localhost:18443/bridge/`
- Public gateway health: `https://localhost:18443/bridge/health`
- Middleware UI: `http://localhost:18082/`
- Healthcheck: `http://localhost:18082/health`
- Links API: `http://localhost:18082/links`
- Link lookup: `http://localhost:18082/links/lookup`
- Link upsert: `http://localhost:18082/links/upsert`
- Link update via form: `POST http://localhost:18082/links/<id>/update`
- Link update via API: `PATCH/PUT http://localhost:18082/links/<id>`
- Filtered links: `http://localhost:18082/links?view=signed`
- Filtered links: `http://localhost:18082/links?view=problem`
- NauDoc: `http://localhost:18080/docs`
- Rukovoditel: `http://localhost:18081/`

Public unified URLs through the gateway:

- Rukovoditel: `https://localhost:18443/`
- NauDoc: `https://localhost:18443/docs/`
- Middleware: `https://localhost:18443/bridge/`

## Start

```bash
cd /home/lebedeffson/Code/Документооборот/middleware
docker compose up -d --build
```

Start the unified gateway:

```bash
cd /home/lebedeffson/Code/Документооборот/gateway
docker compose up -d --build
```

## Example request

```bash
curl -X POST http://localhost:18082/links/upsert \
  -H 'Content-Type: application/json' \
  -d '{
    "external_system": "rukovoditel",
    "external_entity": "service_requests",
    "external_item_id": "101",
    "external_title": "Заявка на обслуживание #101",
    "naudoc_url": "",
    "naudoc_title": "Карточка документа по заявке #101",
    "sync_status": "pending_nau_doc",
    "notes": "Карточка создана, ссылка на NauDoc появится позже",
    "metadata": {"department": "IT", "doc_card_id": 55}
  }'
```

## Current limitations

- there is no direct write-back into `NauDoc` yet
- sync currently covers the first round-trip scenario: `service request -> document card -> bridge -> Rukovoditel`
- intended as the first working integration layer for the test stand
- restore automation exists, but destructive restore was not run on the live stand yet
