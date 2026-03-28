#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from runtime_config import (
    ADMIN_USERNAME,
    EMPLOYEE_USERNAME,
    MANAGER_USERNAME,
    NURSE_USERNAME,
    OFFICE_USERNAME,
    REQUESTER_USERNAME,
)


def load_env(root_dir: Path) -> None:
    env_file = os.environ.get("DOCFLOW_ENV_FILE", str(root_dir / ".env"))
    path = Path(env_file)
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def bridge_base_url() -> str:
    port = os.environ.get("BRIDGE_BIND_PORT", "18082")
    return f"http://127.0.0.1:{port}"


def request_json(url: str, *, payload: dict | None = None, timeout: int = 20):
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        url,
        data=body,
        headers=headers,
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.getcode(), json.loads(response.read().decode("utf-8"))


def main() -> int:
    root_dir = Path(__file__).resolve().parents[1]
    load_env(root_dir)

    base_url = bridge_base_url()
    report = {
        "status": "ok",
        "source_key": "hospital_ldap",
        "bridge_base_url": base_url,
        "issues": [],
        "checks": [],
    }

    try:
        _, sources = request_json(f"{base_url}/identity-sources", timeout=15)
    except Exception as exc:
        report["status"] = "error"
        report["issues"].append(f"bridge identity-sources API failed: {exc}")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    source = next((item for item in sources if item.get("source_key") == "hospital_ldap"), None)
    if source is None:
        report["status"] = "error"
        report["issues"].append("hospital_ldap source is missing")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    report["checks"].append("hospital_ldap source exists")

    if not source.get("is_active"):
        report["status"] = "skipped"
        report["checks"].append("hospital_ldap source is inactive, LDAP audit skipped")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if source.get("provider_type") != "ldap":
        report["status"] = "error"
        report["issues"].append(f"hospital_ldap provider_type must be ldap, got {source.get('provider_type')!r}")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    try:
        test_status, test_payload = request_json(
            f"{base_url}/identity-sources/{source['id']}/test",
            payload={},
            timeout=20,
        )
    except Exception as exc:
        report["status"] = "error"
        report["issues"].append(f"identity source test request failed: {exc}")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    if test_status != 200 or not test_payload.get("ok"):
        report["status"] = "error"
        report["issues"].append(f"identity source test failed: {test_payload}")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    report["checks"].append("LDAP bind test passed")

    try:
        sync_status, sync_payload = request_json(
            f"{base_url}/identity-sources/{source['id']}/sync",
            payload={},
            timeout=30,
        )
    except Exception as exc:
        report["status"] = "error"
        report["issues"].append(f"identity source sync request failed: {exc}")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    if sync_status != 200 or sync_payload.get("status") != "ok":
        report["status"] = "error"
        report["issues"].append(f"identity source sync failed: {sync_payload}")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    report["checks"].append(f"LDAP sync passed: synced={sync_payload.get('synced_count', 0)}")

    try:
        query = urllib.parse.urlencode({"source_system": "ldap"})
        _, profiles = request_json(
            f"{base_url}/user-profiles?{query}",
            timeout=15,
        )
    except Exception as exc:
        report["status"] = "error"
        report["issues"].append(f"user-profiles API failed: {exc}")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    usernames = {item.get("source_username") for item in profiles}
    expected = {
        ADMIN_USERNAME,
        MANAGER_USERNAME,
        EMPLOYEE_USERNAME,
        NURSE_USERNAME,
        REQUESTER_USERNAME,
        OFFICE_USERNAME,
    }
    missing = sorted(expected - usernames)
    if missing:
        report["status"] = "error"
        report["issues"].append(f"missing LDAP profiles: {', '.join(missing)}")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    matched = sum(1 for item in profiles if item.get("sync_status") == "matched")
    report["checks"].append(f"LDAP profiles present: {len(profiles)}")
    report["checks"].append(f"Matched LDAP profiles: {matched}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
