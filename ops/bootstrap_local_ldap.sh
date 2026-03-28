#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# shellcheck source=lib/runtime_env.sh
source "${SCRIPT_DIR}/lib/runtime_env.sh"
docflow_load_env "${ROOT_DIR}"
docflow_export_runtime

ENV_FILE="$(docflow_env_file_path "${ROOT_DIR}")"
if [ ! -f "${ENV_FILE}" ]; then
  echo "[ldap-bootstrap] missing env file: ${ENV_FILE}" >&2
  exit 1
fi

domain_to_base_dn() {
  python3 - "$1" <<'PY'
import sys
domain = sys.argv[1].strip().strip(".")
parts = [part for part in domain.split(".") if part]
print(",".join(f"dc={part}" for part in parts))
PY
}

ensure_env_value() {
  local key="$1"
  local default_value="$2"
  local current_value="${!key:-}"
  local has_env_key="0"
  if grep -q "^${key}=" "${ENV_FILE}" 2>/dev/null; then
    has_env_key="1"
  fi
  if [ -z "${current_value}" ]; then
    current_value="${default_value}"
  fi
  if [ "${has_env_key}" != "1" ]; then
    docflow_set_env_value "${ENV_FILE}" "${key}" "${current_value}"
  fi
  export "${key}=${current_value}"
}

ensure_env_value "LDAP_DOMAIN" "${LDAP_DOMAIN:-hospital.local}"
ensure_env_value "LDAP_ORGANISATION" "${LDAP_ORGANISATION:-Hospital_DocFlow}"
ensure_env_value "LDAP_ADMIN_PASSWORD" "${LDAP_ADMIN_PASSWORD:-$(docflow_random_secret 24)}"
ensure_env_value "LDAP_CONFIG_PASSWORD" "${LDAP_CONFIG_PASSWORD:-$(docflow_random_secret 24)}"
ensure_env_value "LDAP_BIND_PASSWORD" "${LDAP_BIND_PASSWORD:-$(docflow_random_secret 24)}"
ensure_env_value "LDAP_CONTAINER_NAME" "${LDAP_CONTAINER_NAME:-docflow_hospital_ldap}"

LDAP_BASE_DN="$(domain_to_base_dn "${LDAP_DOMAIN}")"
LDAP_USERS_DN="ou=Users,${LDAP_BASE_DN}"
LDAP_GROUPS_DN="ou=Groups,${LDAP_BASE_DN}"
LDAP_SERVICE_ACCOUNTS_DN="ou=Service Accounts,${LDAP_BASE_DN}"
LDAP_BIND_DN="cn=svc-docflow,${LDAP_SERVICE_ACCOUNTS_DN}"
LDAP_SYNC_BIND_DN="cn=admin,${LDAP_BASE_DN}"

TEMPLATE_PATH="${ROOT_DIR}/middleware/ldap/bootstrap/50-hospital-users.ldif.template"
GENERATED_DIR="${ROOT_DIR}/middleware/runtime/ldap/bootstrap"
GENERATED_LDIF="${GENERATED_DIR}/50-hospital-users.ldif"

ensure_writable_dir() {
  local target_dir="$1"
  mkdir -p "${target_dir}" 2>/dev/null || true

  if [ -w "${target_dir}" ]; then
    return 0
  fi

  if ! command -v docker >/dev/null 2>&1; then
    echo "[ldap-bootstrap] ${target_dir} is not writable and docker is unavailable" >&2
    return 1
  fi

  docker run --rm --entrypoint bash -u 0:0 -v "${ROOT_DIR}:/workspace" "${NAUDOC_LEGACY_IMAGE:-docflow/naudoc-legacy:local}" -lc \
    "mkdir -p '/workspace/${target_dir#${ROOT_DIR}/}' && chown -R $(id -u):$(id -g) '/workspace/${target_dir#${ROOT_DIR}/}'" >/dev/null

  if [ ! -w "${target_dir}" ]; then
    echo "[ldap-bootstrap] failed to make ${target_dir} writable" >&2
    return 1
  fi
}

ensure_writable_dir "${GENERATED_DIR}"

python3 - "${TEMPLATE_PATH}" "${GENERATED_LDIF}" "${LDAP_BASE_DN}" "${LDAP_BIND_PASSWORD}" <<'PY'
from pathlib import Path
import os
import sys

template_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
base_dn = sys.argv[3]
bind_password = sys.argv[4]

content = template_path.read_text(encoding="utf-8")
replacements = {
    "__LDAP_BASE_DN__": base_dn,
    "__LDAP_BIND_PASSWORD__": bind_password,
    "__DOCFLOW_MANAGER_USERNAME__": os.environ.get("DOCFLOW_MANAGER_USERNAME", "department.head"),
    "__DOCFLOW_EMPLOYEE_USERNAME__": os.environ.get("DOCFLOW_EMPLOYEE_USERNAME", "clinician.primary"),
    "__DOCFLOW_NURSE_USERNAME__": os.environ.get("DOCFLOW_NURSE_USERNAME", "nurse.coordinator"),
    "__DOCFLOW_REQUESTER_USERNAME__": os.environ.get("DOCFLOW_REQUESTER_USERNAME", "registry.operator"),
    "__DOCFLOW_OFFICE_USERNAME__": os.environ.get("DOCFLOW_OFFICE_USERNAME", "records.office"),
}

for key, value in replacements.items():
    content = content.replace(key, value)

output_path.write_text(content, encoding="utf-8")
PY

echo "[ldap-bootstrap] generated LDIF: ${GENERATED_LDIF}"

docker compose \
  --project-directory "${ROOT_DIR}/middleware" \
  -p "${MIDDLEWARE_COMPOSE_PROJECT_NAME}" \
  --env-file "${ENV_FILE}" \
  -f "${ROOT_DIR}/middleware/docker-compose.yml" \
  --profile identity \
  up -d hospital_ldap middleware

python3 - "${ROOT_DIR}" "${LDAP_CONTAINER_NAME}" "${LDAP_SYNC_BIND_DN}" "${LDAP_ADMIN_PASSWORD}" <<'PY'
import subprocess
import sys
import time

root_dir, container_name, bind_dn, bind_password = sys.argv[1:5]
command = [
    "docker",
    "exec",
    container_name,
    "ldapwhoami",
    "-x",
    "-H",
    "ldap://127.0.0.1:389",
    "-D",
    bind_dn,
    "-w",
    bind_password,
]

deadline = time.time() + 90
last_error = ""
while time.time() < deadline:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print("[ldap-bootstrap] LDAP bind is healthy")
        sys.exit(0)
    last_error = (result.stderr or result.stdout).strip()
    time.sleep(3)

print(f"[ldap-bootstrap] LDAP bind failed: {last_error}", file=sys.stderr)
sys.exit(1)
PY

for dn in "${LDAP_USERS_DN}" "${LDAP_GROUPS_DN}" "${LDAP_SERVICE_ACCOUNTS_DN}"; do
  docker exec "${LDAP_CONTAINER_NAME}" sh -lc \
    "ldapdelete -r -x -H ldap://127.0.0.1:389 -D '${LDAP_SYNC_BIND_DN}' -w '${LDAP_ADMIN_PASSWORD}' '${dn}' >/tmp/ldapdelete.log 2>&1 || true"
done
echo "[ldap-bootstrap] cleared previous local LDAP baseline entries"

docker cp "${GENERATED_LDIF}" "${LDAP_CONTAINER_NAME}:/tmp/50-hospital-users.ldif" >/dev/null
docker exec "${LDAP_CONTAINER_NAME}" sh -lc \
  "ldapadd -c -x -H ldap://127.0.0.1:389 -D '${LDAP_SYNC_BIND_DN}' -w '${LDAP_ADMIN_PASSWORD}' -f /tmp/50-hospital-users.ldif >/tmp/ldapadd.log 2>&1 || true"
docker exec "${LDAP_CONTAINER_NAME}" sh -lc \
  "ldappasswd -x -H ldap://127.0.0.1:389 -D '${LDAP_SYNC_BIND_DN}' -w '${LDAP_ADMIN_PASSWORD}' -s '${LDAP_BIND_PASSWORD}' '${LDAP_BIND_DN}' >/tmp/ldappasswd.log 2>&1"
docker exec "${LDAP_CONTAINER_NAME}" sh -lc "rm -f /tmp/50-hospital-users.ldif /tmp/ldapadd.log /tmp/ldappasswd.log" >/dev/null
echo "[ldap-bootstrap] service account ensured: ${LDAP_BIND_DN}"

BRIDGE_PORT_VALUE="${BRIDGE_BIND_PORT:-18082}"

python3 - "${BRIDGE_PORT_VALUE}" "${LDAP_BASE_DN}" "${LDAP_USERS_DN}" "${LDAP_GROUPS_DN}" "${LDAP_SYNC_BIND_DN}" <<'PY'
import json
import sys
import urllib.error
import urllib.request

bridge_port, base_dn, users_dn, groups_dn, bind_dn = sys.argv[1:6]
bridge_base = f"http://127.0.0.1:{bridge_port}"

def request_json(url, payload=None, timeout=20):
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method="POST" if payload is not None else "GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))

sources = request_json(f"{bridge_base}/identity-sources")
source = next((item for item in sources if item.get("source_key") == "hospital_ldap"), None)
if source is None:
    raise SystemExit("hospital_ldap source not found in Bridge")

payload = {
    "source_key": source["source_key"],
    "source_label": "Корпоративный LDAP/AD",
    "provider_type": "ldap",
    "source_system": "ldap",
    "sync_mode": "sso",
    "host": "hospital_ldap",
    "port": 389,
    "ssl_mode": "none",
    "base_dn": base_dn,
    "user_base_dn": users_dn,
    "group_base_dn": groups_dn,
    "login_attribute": "uid",
    "display_name_attribute": "displayName",
    "email_attribute": "mail",
    "department_attribute": "ou",
    "role_attribute": "title",
    "bind_dn": bind_dn,
    "bind_password_env_key": "LDAP_ADMIN_PASSWORD",
    "notes": "Локальный production-like LDAP стенда для hospital pilot и staging. Для реального LDAP/AD bind DN затем меняется в GUI на сервисный аккаунт svc-docflow.",
    "metadata": {"search_filter": "(objectClass=inetOrgPerson)", "sync_limit": 200, "profile_url_template": "ldap://hospital_ldap/{username}"},
    "is_active": True,
    "is_default": False,
}

request_json(f"{bridge_base}/identity-sources/{source['id']}/update", payload=payload)
print("[ldap-bootstrap] bridge source configured")

test_payload = request_json(f"{bridge_base}/identity-sources/{source['id']}/test", payload={})
print("[ldap-bootstrap] test:", test_payload)

sync_payload = request_json(f"{bridge_base}/identity-sources/{source['id']}/sync", payload={})
print("[ldap-bootstrap] sync:", sync_payload)
PY

docker exec -i "${BRIDGE_CONTAINER}" python3 - \
  "${DOCFLOW_ADMIN_USERNAME}" \
  "${DOCFLOW_MANAGER_USERNAME}" \
  "${DOCFLOW_EMPLOYEE_USERNAME}" \
  "${DOCFLOW_NURSE_USERNAME}" \
  "${DOCFLOW_REQUESTER_USERNAME}" \
  "${DOCFLOW_OFFICE_USERNAME}" <<'PY'
import sqlite3
import sys

expected_usernames = tuple(dict.fromkeys(arg.strip() for arg in sys.argv[1:] if arg.strip()))
if not expected_usernames:
    print("[ldap-bootstrap] bridge cleanup skipped: no expected usernames")
    raise SystemExit(0)

placeholders = ",".join("?" for _ in expected_usernames)
with sqlite3.connect("/data/bridge.db") as conn:
    cursor = conn.execute(
        f"DELETE FROM user_directory_profiles WHERE source_system = 'ldap' AND source_username NOT IN ({placeholders})",
        expected_usernames,
    )
    conn.commit()
    print(f"[ldap-bootstrap] removed stale LDAP profiles from Bridge: {cursor.rowcount}")
PY

echo "[ldap-bootstrap] local LDAP baseline is ready"
