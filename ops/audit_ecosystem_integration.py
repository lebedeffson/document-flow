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
]

EXPECTED_BRIDGE_METADATA = [
    {
        "external_entity": "service_requests",
        "external_item_id": "1",
        "metadata_keys": [
            "request_url",
            "doc_card_url",
        ],
    },
    {
        "external_entity": "projects",
        "external_item_id": "1",
        "metadata_keys": [
            "project_url",
            "doc_card_url",
        ],
    },
    {
        "external_entity": "document_cards",
        "external_item_id": "1",
        "metadata_keys": [
            "doc_card_url",
            "source_request_url",
        ],
    },
    {
        "external_entity": "document_cards",
        "external_item_id": "2",
        "metadata_keys": [
            "doc_card_url",
            "source_project_url",
        ],
    },
]


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

        if not isinstance(metadata, dict):
            missing_keys = list(bridge_case["metadata_keys"])
        else:
            for key in bridge_case["metadata_keys"]:
                if not metadata.get(key):
                    missing_keys.append(key)

        bridge_result = {
            "external_entity": bridge_case["external_entity"],
            "external_item_id": bridge_case["external_item_id"],
            "status": status,
            "missing_keys": missing_keys,
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

    print(json.dumps(results, ensure_ascii=False, indent=2))

    if results["failures"]:
        return 1

    print("[audit] ecosystem integration is healthy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
