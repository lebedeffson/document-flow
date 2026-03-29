#!/usr/bin/env python3
import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from runtime_config import (
    BRIDGE_BASE,
    DOCSPACE_BASE,
    DOCSPACE_ENABLED,
    DOCSPACE_TARGET_URL,
    GATEWAY_BASE,
    LOCAL_PROBE_IP,
    OFFICE_BASE,
    ROOT_DIR,
    WORKSPACE_BASE,
    WORKSPACE_ENABLED,
    WORKSPACE_TARGET_URL,
)


SSL_CONTEXT = ssl._create_unverified_context()


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


NO_REDIRECT_OPENER = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=SSL_CONTEXT),
    NoRedirectHandler(),
)


def build_probe_request(url: str):
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.hostname or not LOCAL_PROBE_IP:
        return urllib.request.Request(url)

    netloc = LOCAL_PROBE_IP
    if parsed.port:
        netloc = f"{LOCAL_PROBE_IP}:{parsed.port}"

    probe_url = urlunparse(
        (
            parsed.scheme,
            netloc,
            parsed.path or "/",
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )

    request = urllib.request.Request(probe_url)
    request.add_header("Host", parsed.netloc)
    return request


def fetch_text(url: str):
    request = build_probe_request(url)
    try:
        with NO_REDIRECT_OPENER.open(request, timeout=10) as response:
            return response.status, response.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "ignore")
    except Exception as exc:
        return None, str(exc)


def fetch_direct_text(url: str):
    parsed = urlparse(url)
    if parsed.hostname in {"host.docker.internal", "localhost"} or (parsed.hostname or "").startswith("127."):
        request = build_probe_request(url)
    else:
        request = urllib.request.Request(url)
    try:
        with NO_REDIRECT_OPENER.open(request, timeout=10) as response:
            return response.status, response.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "ignore")
    except Exception as exc:
        return None, str(exc)


def fetch_json(url: str):
    status, body = fetch_text(url)
    if status is None:
        return status, None
    try:
        return status, json.loads(body)
    except Exception:
        return status, None


def acceptable_remote_status(status: int | None):
    return status in (200, 301, 302, 401, 403)


def latest_backup_info():
    backups_dir = ROOT_DIR / "backups"
    if not backups_dir.exists():
        return {"exists": False, "latest": None, "age_hours": None}

    candidates = [item for item in backups_dir.iterdir() if item.is_dir()]
    if not candidates:
        return {"exists": True, "latest": None, "age_hours": None}

    latest = max(candidates, key=lambda item: item.stat().st_mtime)
    latest_dt = datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
    age_hours = round((datetime.now(timezone.utc) - latest_dt).total_seconds() / 3600, 2)
    return {
        "exists": True,
        "latest": str(latest),
        "age_hours": age_hours,
    }


def main():
    parser = argparse.ArgumentParser(description="Capture a lightweight operational snapshot for DocFlow.")
    parser.add_argument(
        "--output",
        default=str(ROOT_DIR / "runtime" / "monitoring" / "latest_status.json"),
        help="Path to the JSON output file.",
    )
    args = parser.parse_args()

    gateway_status, gateway_body = fetch_text(f"{GATEWAY_BASE}/healthz")
    bridge_status, bridge_payload = fetch_json(f"{BRIDGE_BASE}/health")
    office_status, office_body = fetch_text(f"{OFFICE_BASE}/healthcheck")
    docspace_status, _ = fetch_text(f"{DOCSPACE_BASE}/")
    workspace_status, _ = fetch_text(f"{WORKSPACE_BASE}/")
    docspace_target_status = None
    workspace_target_status = None

    if DOCSPACE_TARGET_URL:
        docspace_target_status, _ = fetch_direct_text(DOCSPACE_TARGET_URL)

    if WORKSPACE_TARGET_URL:
        workspace_target_status, _ = fetch_direct_text(WORKSPACE_TARGET_URL)

    failures_status, failures_payload = fetch_json(f"{BRIDGE_BASE}/sync-failures?status=open")
    profiles_status, profiles_payload = fetch_json(f"{BRIDGE_BASE}/user-profiles")

    gateway_ok = gateway_status == 200 and gateway_body.strip().lower() == "ok"
    bridge_ok = bridge_status == 200 and isinstance(bridge_payload, dict) and bridge_payload.get("status") == "ok"
    office_ok = office_status == 200 and office_body.strip().lower() == "true"
    docspace_ok = (not DOCSPACE_ENABLED) or (
        acceptable_remote_status(docspace_status) and (not DOCSPACE_TARGET_URL or acceptable_remote_status(docspace_target_status))
    )
    workspace_ok = (not WORKSPACE_ENABLED) or (
        acceptable_remote_status(workspace_status) and (not WORKSPACE_TARGET_URL or acceptable_remote_status(workspace_target_status))
    )

    open_failures = len(failures_payload) if isinstance(failures_payload, list) else None
    unmatched_profiles = None
    if isinstance(profiles_payload, list):
        unmatched_profiles = sum(1 for item in profiles_payload if item.get("sync_status") != "matched")

    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "public_base": GATEWAY_BASE,
        "gateway": {
            "status_code": gateway_status,
            "ok": gateway_ok,
        },
        "bridge": {
            "status_code": bridge_status,
            "ok": bridge_ok,
            "links_total": bridge_payload.get("links_total") if isinstance(bridge_payload, dict) else None,
        },
        "onlyoffice": {
            "status_code": office_status,
            "ok": office_ok,
        },
        "office_ecosystem": {
            "docspace": {
                "enabled": DOCSPACE_ENABLED,
                "status_code": docspace_status,
                "frontdoor_status_code": docspace_status,
                "target_status_code": docspace_target_status,
                "ok": docspace_ok,
                "target_configured": bool(DOCSPACE_TARGET_URL),
                "mode": "live_target" if DOCSPACE_TARGET_URL else ("shell_only" if DOCSPACE_ENABLED else "disabled"),
            },
            "workspace": {
                "enabled": WORKSPACE_ENABLED,
                "status_code": workspace_status,
                "frontdoor_status_code": workspace_status,
                "target_status_code": workspace_target_status,
                "ok": workspace_ok,
                "target_configured": bool(WORKSPACE_TARGET_URL),
                "mode": "live_target" if WORKSPACE_TARGET_URL else ("shell_only" if WORKSPACE_ENABLED else "disabled"),
            },
        },
        "sync": {
            "open_failures": open_failures,
            "source_status_code": failures_status,
        },
        "users": {
            "unmatched_profiles": unmatched_profiles,
            "source_status_code": profiles_status,
        },
        "backups": latest_backup_info(),
    }

    core_ok = gateway_ok and bridge_ok and office_ok and docspace_ok and workspace_ok
    result["status"] = "ok" if core_ok and (open_failures in (0, None)) else "warning"

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if core_ok else 1


if __name__ == "__main__":
    sys.exit(main())
