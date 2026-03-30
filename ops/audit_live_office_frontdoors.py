#!/usr/bin/env python3
import json
import re
import ssl
import sys
import urllib.request
from urllib.error import HTTPError, URLError

from runtime_config import DOCSPACE_BASE, WORKSPACE_BASE, DOCSPACE_ENABLED, WORKSPACE_ENABLED


CTX = ssl._create_unverified_context()


def fetch(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": "docflow-audit/1.0"})

    try:
      with urllib.request.urlopen(request, context=CTX, timeout=30) as response:
          body = response.read(4096).decode("utf-8", "ignore")
          return {
              "ok": True,
              "status": int(getattr(response, "status", 200)),
              "final_url": response.geturl(),
              "body": body,
          }
    except HTTPError as exc:
      body = exc.read(4096).decode("utf-8", "ignore")
      return {
          "ok": False,
          "status": int(exc.code),
          "final_url": exc.geturl(),
          "body": body,
      }
    except URLError as exc:
      return {
          "ok": False,
          "status": None,
          "final_url": url,
          "body": "",
          "error": str(exc.reason),
      }


def audit_docspace():
    result = fetch(f"{DOCSPACE_BASE}/")
    failures = []

    if not result["status"] or result["status"] >= 400:
        failures.append(f"DocSpace frontdoor returned bad status: {result['status']}")

    if not result["final_url"].startswith(f"{DOCSPACE_BASE}/"):
        failures.append(f"DocSpace final url escaped frontdoor: {result['final_url']}")

    body = result.get("body", "")
    if "logo.ashx" not in body and "DocSpace" not in body and "/docspace/" not in body:
        failures.append("DocSpace body does not look like a DocSpace page")

    return {
        "name": "docspace_frontdoor",
        "enabled": DOCSPACE_ENABLED,
        "status": result.get("status"),
        "final_url": result.get("final_url"),
        "ok": not failures,
        "failures": failures,
    }


def audit_workspace():
    result = fetch(f"{WORKSPACE_BASE}/")
    failures = []

    if not result["status"] or result["status"] >= 400:
        failures.append(f"Workspace frontdoor returned bad status: {result['status']}")

    expected_prefixes = [f"{WORKSPACE_BASE}/", f"{WORKSPACE_BASE}/Wizard.aspx"]
    if not any(result["final_url"].startswith(prefix) for prefix in expected_prefixes):
        failures.append(f"Workspace final url escaped frontdoor: {result['final_url']}")

    body = result.get("body", "")
    if not re.search(r"Portal Setup|ONLYOFFICE|/workspace/", body, re.I):
        failures.append("Workspace body does not look like a Workspace page")

    return {
        "name": "workspace_frontdoor",
        "enabled": WORKSPACE_ENABLED,
        "status": result.get("status"),
        "final_url": result.get("final_url"),
        "ok": not failures,
        "failures": failures,
    }


def main():
    checks = []

    if DOCSPACE_ENABLED:
        checks.append(audit_docspace())

    if WORKSPACE_ENABLED:
        checks.append(audit_workspace())

    failures = [failure for check in checks for failure in check["failures"]]
    payload = {
        "status": "ok" if not failures else "failed",
        "checks": checks,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
