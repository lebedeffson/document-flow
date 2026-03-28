#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# shellcheck source=lib/runtime_env.sh
source "${ROOT_DIR}/ops/lib/runtime_env.sh"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

RUKOVODITEL_URL="${DOCFLOW_PUBLIC_BASE}/index.php?module=dashboard/"

curl_docflow() {
  local url="${1:-}"
  shift || true

  local scheme host port path probe_ip
  scheme="$(docflow_url_field "${url}" scheme)"
  host="$(docflow_url_field "${url}" host)"
  port="$(docflow_url_field "${url}" port)"
  path="$(docflow_url_field "${url}" path)"
  probe_ip="$(docflow_local_probe_ip)"

  if [[ -z "${scheme}" || -z "${host}" || -z "${port}" ]]; then
    echo "[smoke] ERROR: failed to parse url: ${url}" >&2
    return 1
  fi

  curl --resolve "${host}:${port}:${probe_ip}" "$@" "${scheme}://${host}:${port}${path}"
}

echo "[smoke] stack health"
bash ops/check_stack.sh >/tmp/dms_check_stack.log
tail -n +1 /tmp/dms_check_stack.log

echo
echo "[smoke] rukovoditel login via gateway"
COOKIE_JAR="$(mktemp)"
LOGIN_PAGE="$(mktemp)"
LOGIN_BODY="$(mktemp)"
curl_docflow "${DOCFLOW_PUBLIC_BASE}/index.php?module=dashboard/" -k -sS -L -c "${COOKIE_JAR}" -b "${COOKIE_JAR}" > "${LOGIN_PAGE}"

LOGIN_TOKEN="$(python3 - "${LOGIN_PAGE}" <<'PY'
from pathlib import Path
import re
import sys

html = Path(sys.argv[1]).read_text(encoding="utf-8", errors="ignore")
match = re.search(r'name="form_session_token" id="form_session_token" value="([^"]+)"', html)
print(match.group(1) if match else "", end="")
PY
)"

if [ -z "${LOGIN_TOKEN}" ]; then
  echo "Rukovoditel login token not found" >&2
  exit 1
fi

LOGIN_FINAL_URL="$(
  curl_docflow "${DOCFLOW_PUBLIC_BASE}/index.php?module=users/login&action=login" \
    -k -sS -L \
    -c "${COOKIE_JAR}" \
    -b "${COOKIE_JAR}" \
    -o "${LOGIN_BODY}" \
    -w '%{url_effective}' \
    --data-urlencode "form_session_token=${LOGIN_TOKEN}" \
    --data-urlencode "username=${DOCFLOW_ADMIN_USERNAME:-admin}" \
    --data-urlencode "password=${DOCFLOW_ADMIN_PASSWORD:-admin123}"
)"

python3 - "${LOGIN_BODY}" "${LOGIN_FINAL_URL}" <<'PY'
from pathlib import Path
import sys

body = Path(sys.argv[1]).read_text(encoding="utf-8", errors="ignore")
required = [
    "Главная",
    "Работа",
    "Документы",
    "Контроль",
]
missing = [item for item in required if item not in body]
print("final_url:", sys.argv[2])
print("missing_menu_items:", missing)
if missing:
    sys.exit(1)
PY

echo
echo "[smoke] onlyoffice through gateway"
curl_docflow "${DOCFLOW_OFFICE_PUBLIC_BASE}/healthcheck" -k -sf >/dev/null
curl_docflow "${DOCFLOW_OFFICE_PUBLIC_BASE}/web-apps/apps/api/documents/api.js" -k -sf >/tmp/dms_onlyoffice_api.js
if ! rg -q 'DocsAPI|DocEditor' /tmp/dms_onlyoffice_api.js; then
  echo "ONLYOFFICE api.js does not look correct" >&2
  exit 1
fi
echo "onlyoffice api.js available"

echo
echo "[smoke] naudoc through gateway"
NAUDOC_INDEX="$(mktemp)"
NAUDOC_HOME="$(mktemp)"
curl_docflow "${DOCFLOW_DOCS_BASE}/" -k -s -u "${NAUDOC_USERNAME}:${NAUDOC_PASSWORD}" >"$NAUDOC_INDEX"
curl_docflow "${DOCFLOW_DOCS_BASE}/home" -k -s -u "${NAUDOC_USERNAME}:${NAUDOC_PASSWORD}" >"$NAUDOC_HOME"
curl_docflow "${DOCFLOW_DOCS_BASE}/inFrame?link=member_tasks" -k -sf -u "${NAUDOC_USERNAME}:${NAUDOC_PASSWORD}" >/dev/null
curl_docflow "${DOCFLOW_DOCS_BASE}/storage/view" -k -sf -u "${NAUDOC_USERNAME}:${NAUDOC_PASSWORD}" >/dev/null

if rg -q 'host\.docker\.internal' "$NAUDOC_INDEX" "$NAUDOC_HOME" || rg -Fq "http://${DOCFLOW_DOCS_BASE#https://}" "$NAUDOC_INDEX" "$NAUDOC_HOME"; then
  echo "NauDoc still exposes internal or insecure public URLs" >&2
  exit 1
fi

if ! rg -Fq "${DOCFLOW_DOCS_BASE}" "$NAUDOC_INDEX" "$NAUDOC_HOME"; then
  echo "NauDoc gateway pages do not contain the expected public https docs URL" >&2
  exit 1
fi

echo "naudoc gateway pages normalized"

echo
echo "[smoke] sync scripts"
bash rukovoditel-test/sync_service_requests.sh >/tmp/dms_sync_requests.log
bash rukovoditel-test/sync_project_documents.sh >/tmp/dms_sync_projects.log
bash rukovoditel-test/sync_document_cards.sh --force-all >/tmp/dms_sync_doc_cards.log
bash rukovoditel-test/pull_bridge_updates.sh --only-linked >/tmp/dms_pull_bridge.log
cat /tmp/dms_sync_requests.log
cat /tmp/dms_sync_projects.log
cat /tmp/dms_sync_doc_cards.log
cat /tmp/dms_pull_bridge.log

echo
echo "[smoke] bridge links"
BRIDGE_LINKS_JSON="$(mktemp)"
curl_docflow "${DOCFLOW_BRIDGE_PUBLIC_BASE}/links" -k -sS -f > "${BRIDGE_LINKS_JSON}"
python3 - "${BRIDGE_LINKS_JSON}" "${DOCFLOW_DOCS_BASE}" <<'PY'
import json
from pathlib import Path
import sys

links = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
docs_base = sys.argv[2]
print("links_total:", len(links))
if len(links) < 4:
    print("Expected at least 4 integration links", file=sys.stderr)
    sys.exit(1)

bad = []
for link in links:
    url = link.get("naudoc_url", "")
    if url and not url.startswith(docs_base):
        bad.append((link.get("id"), url))

print("non_public_naudoc_urls:", bad)
if bad:
    sys.exit(1)
PY

echo
echo "[smoke] rukovoditel data consistency"
docker exec "${RUKOVODITEL_DB_CONTAINER}" mariadb -N -u"${RUKOVODITEL_DB_USER}" -p"${RUKOVODITEL_DB_PASSWORD}" "${RUKOVODITEL_DB_NAME}" <<SQL
SELECT 'requests', COUNT(*) FROM app_entity_23;
SELECT 'projects', COUNT(*) FROM app_entity_21;
SELECT 'doc_cards', COUNT(*) FROM app_entity_25;
SELECT 'request_urls_not_public', COUNT(*) FROM app_entity_23 WHERE length(field_241) > 0 AND field_241 NOT LIKE '${DOCFLOW_DOCS_BASE}%';
SELECT 'project_urls_not_public', COUNT(*) FROM app_entity_21 WHERE length(field_230) > 0 AND field_230 NOT LIKE '${DOCFLOW_DOCS_BASE}%';
SELECT 'doc_urls_not_public', COUNT(*) FROM app_entity_25 WHERE length(field_250) > 0 AND field_250 NOT LIKE '${DOCFLOW_DOCS_BASE}%';
SELECT 'onlyoffice_fields_doc_cards', COUNT(*) FROM app_fields WHERE entities_id=25 AND type='fieldtype_onlyoffice';
SQL

echo
echo "[smoke] done"
