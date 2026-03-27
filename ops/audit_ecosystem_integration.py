#!/usr/bin/env python3
import json
import sys
import urllib.parse

from full_contour_audit import GATEWAY_BASE, BRIDGE_BASE, decode_html, http_get, login_rukovoditel


EXPECTED_PAGES = [
    {
        "name": "document_card",
        "url": f"{GATEWAY_BASE}/index.php?module=items/info&path=25-1",
        "contains": ["Быстрые действия", "Открыть документ в редакторе", "Открыть в NauDoc"],
        "not_contains": ["Открыть DocSpace", "Открыть Workspace"],
    },
    {
        "name": "project_card",
        "url": f"{GATEWAY_BASE}/index.php?module=items/info&path=21-1",
        "contains": ["Быстрые действия", "Открыть в NauDoc"],
        "not_contains": ["Открыть DocSpace", "Открыть Workspace"],
    },
    {
        "name": "request_card",
        "url": f"{GATEWAY_BASE}/index.php?module=items/info&path=23-1",
        "contains": ["Быстрые действия", "Открыть в NauDoc"],
        "not_contains": ["Открыть DocSpace", "Открыть Workspace"],
    },
    {
        "name": "documents_listing",
        "url": f"{GATEWAY_BASE}/index.php?module=items/items&path=25",
        "contains": ["Открыть демонстрационный документ", "Открыть NauDoc"],
        "not_contains": ["Открыть DocSpace", "Открыть Workspace"],
    },
    {
        "name": "document_base_card",
        "url": f"{GATEWAY_BASE}/index.php?module=items/info&path=26-1",
        "contains": ["Быстрые действия", "Открыть в NauDoc"],
        "not_contains": ["Открыть DocSpace", "Открыть Workspace"],
    },
    {
        "name": "document_base_listing",
        "url": f"{GATEWAY_BASE}/index.php?module=items/items&path=26",
        "contains": ["База документов", "Открыть NauDoc"],
        "not_contains": ["Открыть DocSpace", "Открыть Workspace"],
    },
    {
        "name": "mts_card",
        "url": f"{GATEWAY_BASE}/index.php?module=items/info&path=27-1",
        "contains": ["Быстрые действия", "Открыть в NauDoc"],
        "not_contains": ["Открыть DocSpace", "Открыть Workspace"],
    },
    {
        "name": "mts_listing",
        "url": f"{GATEWAY_BASE}/index.php?module=items/items&path=27",
        "contains": ["Заявки на МТЗ", "Открыть NauDoc"],
        "not_contains": ["Открыть DocSpace", "Открыть Workspace"],
    },
    {
        "name": "bridge_directory_admin",
        "url": f"{BRIDGE_BASE}/",
        "contains": ["Каталог пользователей", "Источники идентификации", "Hospital-роли", "Маппинг полей"],
        "not_contains": [],
    },
]

EXPECTED_BRIDGE_METADATA = [
    {
        "external_entity": "service_requests",
        "external_item_id": "1",
        "metadata_keys": [
            "request_url",
            "doc_card_url",
        ],
        "projection_keys": [
            ("document", "title"),
            ("document", "source_request_url"),
        ],
    },
    {
        "external_entity": "projects",
        "external_item_id": "1",
        "metadata_keys": [
            "project_url",
            "doc_card_url",
        ],
        "projection_keys": [
            ("document", "title"),
            ("document", "source_project_url"),
        ],
    },
    {
        "external_entity": "document_cards",
        "external_item_id": "1",
        "metadata_keys": [
            "doc_card_url",
            "source_request_url",
        ],
        "projection_keys": [
            ("document", "title"),
            ("document", "source_request_url"),
        ],
    },
    {
        "external_entity": "document_cards",
        "external_item_id": "2",
        "metadata_keys": [
            "doc_card_url",
            "source_project_url",
        ],
        "projection_keys": [
            ("document", "title"),
            ("document", "source_project_url"),
        ],
    },
]

EXPECTED_IDENTITY_SOURCES = {
    "required_source_keys": {"rukovoditel_local", "naudoc_catalog", "hospital_ldap"},
    "required_provider_types": {"local", "external", "ldap"},
}

EXPECTED_HOSPITAL_ROLE_MAPPINGS = {
    "required_hospital_roles": {"hospital_admin", "department_head", "clinician", "registry_operator", "records_office"},
    "required_source_systems": {"rukovoditel"},
}


def fetch_bridge_link(external_entity: str, external_item_id: str):
    params = urllib.parse.urlencode(
        {
            "external_system": "rukovoditel",
            "external_entity": external_entity,
            "external_item_id": external_item_id,
        }
    )
    response, body = http_get(f"{BRIDGE_BASE}/links/lookup?{params}")
    if response.status != 200:
        return response.status, None

    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        return response.status, None

    return response.status, payload


def fetch_bridge_json(path: str):
    response, body = http_get(f"{BRIDGE_BASE}{path}")
    if response.status != 200:
        return response.status, None
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        return response.status, None
    return response.status, payload


def main():
    opener, _, _ = login_rukovoditel("admin", "admin123")
    results = {"pages": [], "bridge_metadata": [], "failures": []}

    for page in EXPECTED_PAGES:
        response, body = http_get(page["url"], opener=opener)
        html = decode_html(body)
        missing = [needle for needle in page["contains"] if needle not in html]
        unexpected = [needle for needle in page.get("not_contains", []) if needle in html]

        page_result = {
            "name": page["name"],
            "url": page["url"],
            "status": response.status,
            "missing": missing,
            "unexpected": unexpected,
        }
        results["pages"].append(page_result)

        if response.status != 200:
            results["failures"].append(f"{page['name']}: unexpected status {response.status}")

        for needle in missing:
            results["failures"].append(f"{page['name']}: missing text '{needle}'")

        for needle in unexpected:
            results["failures"].append(f"{page['name']}: unexpected text '{needle}'")

    for bridge_case in EXPECTED_BRIDGE_METADATA:
        status, payload = fetch_bridge_link(
            bridge_case["external_entity"], bridge_case["external_item_id"]
        )
        metadata = payload.get("metadata") if isinstance(payload, dict) else None
        missing_keys = []
        missing_projection = []

        if not isinstance(metadata, dict):
            missing_keys = list(bridge_case["metadata_keys"])
            missing_projection = list(bridge_case.get("projection_keys", []))
        else:
            for key in bridge_case["metadata_keys"]:
                if not metadata.get(key):
                    missing_keys.append(key)
            projection = metadata.get("naudoc_projection")
            if not isinstance(projection, dict):
                missing_projection = list(bridge_case.get("projection_keys", []))
            else:
                for entity_name, key_name in bridge_case.get("projection_keys", []):
                    entity_payload = projection.get(entity_name)
                    if not isinstance(entity_payload, dict) or not entity_payload.get(key_name):
                        missing_projection.append((entity_name, key_name))

        bridge_result = {
            "external_entity": bridge_case["external_entity"],
            "external_item_id": bridge_case["external_item_id"],
            "status": status,
            "missing_keys": missing_keys,
            "missing_projection": missing_projection,
        }
        results["bridge_metadata"].append(bridge_result)

        if status != 200:
            results["failures"].append(
                f"bridge {bridge_case['external_entity']}#{bridge_case['external_item_id']}: unexpected status {status}"
            )

        for key in missing_keys:
            results["failures"].append(
                f"bridge {bridge_case['external_entity']}#{bridge_case['external_item_id']}: missing metadata '{key}'"
            )
        for entity_name, key_name in missing_projection:
            results["failures"].append(
                f"bridge {bridge_case['external_entity']}#{bridge_case['external_item_id']}: missing naudoc projection '{entity_name}.{key_name}'"
            )

    status, identity_sources = fetch_bridge_json("/identity-sources")
    if status != 200 or not isinstance(identity_sources, list):
        results["failures"].append(f"bridge identity-sources: unexpected status {status}")
    else:
        source_keys = {item.get("source_key") for item in identity_sources}
        provider_types = {item.get("provider_type") for item in identity_sources}
        missing_source_keys = sorted(EXPECTED_IDENTITY_SOURCES["required_source_keys"] - source_keys)
        missing_provider_types = sorted(EXPECTED_IDENTITY_SOURCES["required_provider_types"] - provider_types)
        for key in missing_source_keys:
            results["failures"].append(f"bridge identity-sources: missing source_key '{key}'")
        for provider_type in missing_provider_types:
            results["failures"].append(f"bridge identity-sources: missing provider_type '{provider_type}'")

    status, hospital_role_mappings = fetch_bridge_json("/hospital-role-mappings")
    if status != 200 or not isinstance(hospital_role_mappings, list):
        results["failures"].append(f"bridge hospital-role-mappings: unexpected status {status}")
    else:
        hospital_roles = {item.get("hospital_role_key") for item in hospital_role_mappings}
        source_systems = {item.get("source_system") for item in hospital_role_mappings}
        missing_roles = sorted(EXPECTED_HOSPITAL_ROLE_MAPPINGS["required_hospital_roles"] - hospital_roles)
        missing_systems = sorted(EXPECTED_HOSPITAL_ROLE_MAPPINGS["required_source_systems"] - source_systems)
        for role_key in missing_roles:
            results["failures"].append(f"bridge hospital-role-mappings: missing hospital_role_key '{role_key}'")
        for source_system in missing_systems:
            results["failures"].append(f"bridge hospital-role-mappings: missing source_system '{source_system}'")

    print(json.dumps(results, ensure_ascii=False, indent=2))

    if results["failures"]:
        return 1

    print("[audit] ecosystem integration is healthy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
