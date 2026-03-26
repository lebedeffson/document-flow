#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

RUKOVODITEL_URL="https://localhost:18443/index.php?module=dashboard/"

echo "[smoke] stack health"
bash ops/check_stack.sh >/tmp/dms_check_stack.log
tail -n +1 /tmp/dms_check_stack.log

echo
echo "[smoke] rukovoditel login via gateway"
python3 - <<'PY'
import re
import ssl
import sys
import urllib.parse
import urllib.request
import http.cookiejar

ctx = ssl._create_unverified_context()
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=ctx),
    urllib.request.HTTPCookieProcessor(cj),
)

html = opener.open("https://localhost:18443/index.php?module=dashboard/").read().decode("utf-8", "ignore")
match = re.search(r'name="form_session_token" id="form_session_token" value="([^"]+)"', html)
if not match:
    print("Rukovoditel login token not found", file=sys.stderr)
    sys.exit(1)

payload = urllib.parse.urlencode(
    {
        "form_session_token": match.group(1),
        "username": "admin",
        "password": "admin123",
    }
).encode()
resp = opener.open("https://localhost:18443/index.php?module=users/login&action=login", data=payload)
body = resp.read().decode("utf-8", "ignore")

required = [
    "Главная",
    "Работа",
    "Документы",
    "Контроль",
]
missing = [item for item in required if item not in body]
print("final_url:", resp.geturl())
print("missing_menu_items:", missing)
if missing:
    sys.exit(1)
PY

echo
echo "[smoke] onlyoffice through gateway"
curl -k -sf https://localhost:18443/office/healthcheck >/dev/null
curl -k -sf https://localhost:18443/office/web-apps/apps/api/documents/api.js >/tmp/dms_onlyoffice_api.js
if ! rg -q 'DocsAPI|DocEditor' /tmp/dms_onlyoffice_api.js; then
  echo "ONLYOFFICE api.js does not look correct" >&2
  exit 1
fi
echo "onlyoffice api.js available"

echo
echo "[smoke] naudoc through gateway"
NAUDOC_INDEX="$(mktemp)"
NAUDOC_HOME="$(mktemp)"
curl -k -s -u admin:admin https://localhost:18443/docs/ >"$NAUDOC_INDEX"
curl -k -s -u admin:admin https://localhost:18443/docs/home >"$NAUDOC_HOME"
curl -k -sf -u admin:admin 'https://localhost:18443/docs/inFrame?link=member_tasks' >/dev/null
curl -k -sf -u admin:admin 'https://localhost:18443/docs/storage/view' >/dev/null

if rg -q 'host\.docker\.internal|http://localhost:18443/docs' "$NAUDOC_INDEX" "$NAUDOC_HOME"; then
  echo "NauDoc still exposes internal or insecure public URLs" >&2
  exit 1
fi

if ! rg -q 'https://localhost:18443/docs' "$NAUDOC_INDEX" "$NAUDOC_HOME"; then
  echo "NauDoc gateway pages do not contain the expected public https docs URL" >&2
  exit 1
fi

echo "naudoc gateway pages normalized"

echo
echo "[smoke] sync scripts"
bash rukovoditel-test/sync_service_requests.sh >/tmp/dms_sync_requests.log
bash rukovoditel-test/sync_project_documents.sh >/tmp/dms_sync_projects.log
bash rukovoditel-test/pull_bridge_updates.sh --only-linked >/tmp/dms_pull_bridge.log
cat /tmp/dms_sync_requests.log
cat /tmp/dms_sync_projects.log
cat /tmp/dms_pull_bridge.log

echo
echo "[smoke] bridge links"
python3 - <<'PY'
import json
import ssl
import sys
import urllib.request

ctx = ssl._create_unverified_context()
resp = urllib.request.urlopen("https://localhost:18443/bridge/links", context=ctx)
links = json.loads(resp.read().decode("utf-8"))
print("links_total:", len(links))
if len(links) < 4:
    print("Expected at least 4 integration links", file=sys.stderr)
    sys.exit(1)

bad = []
for link in links:
    url = link.get("naudoc_url", "")
    if url and not url.startswith("https://localhost:18443/docs"):
        bad.append((link.get("id"), url))

print("non_public_naudoc_urls:", bad)
if bad:
    sys.exit(1)
PY

echo
echo "[smoke] rukovoditel data consistency"
docker exec rukovoditel_db_test mariadb -N -urukovoditel -prukovoditel rukovoditel <<'SQL'
SELECT 'requests', COUNT(*) FROM app_entity_23;
SELECT 'projects', COUNT(*) FROM app_entity_21;
SELECT 'doc_cards', COUNT(*) FROM app_entity_25;
SELECT 'request_urls_not_public', COUNT(*) FROM app_entity_23 WHERE length(field_241) > 0 AND field_241 NOT LIKE 'https://localhost:18443/docs%';
SELECT 'project_urls_not_public', COUNT(*) FROM app_entity_21 WHERE length(field_230) > 0 AND field_230 NOT LIKE 'https://localhost:18443/docs%';
SELECT 'doc_urls_not_public', COUNT(*) FROM app_entity_25 WHERE length(field_250) > 0 AND field_250 NOT LIKE 'https://localhost:18443/docs%';
SELECT 'onlyoffice_fields_doc_cards', COUNT(*) FROM app_fields WHERE entities_id=25 AND type='fieldtype_onlyoffice';
SQL

echo
echo "[smoke] done"
