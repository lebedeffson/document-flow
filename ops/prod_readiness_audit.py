#!/usr/bin/env python3
import json
import os
import pathlib
import sys


ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
ENV_FILE = pathlib.Path(os.environ.get("DOCFLOW_ENV_FILE", str(ROOT_DIR / ".env")))


DEFAULTS = {
    "GATEWAY_SERVER_NAME": "localhost",
    "GATEWAY_EXTERNAL_HTTPS_PORT": "18443",
    "GATEWAY_TLS_CN": "localhost",
    "RUKOVODITEL_PUBLIC_URL": "https://localhost:18443",
    "NAUDOC_PUBLIC_URL": "https://localhost:18443/docs",
    "NAUDOC_BASE_URL": "http://host.docker.internal:18080/docs",
    "RUKOVODITEL_BASE_URL": "http://host.docker.internal:18081",
    "ONLYOFFICE_PUBLIC_JS_API_URL": "https://localhost:18443/office/web-apps/apps/api/documents/api.js",
    "RUKOVODITEL_DB_PASSWORD": "rukovoditel",
    "RUKOVODITEL_DB_ROOT_PASSWORD": "root_rukovoditel",
    "NAUDOC_PASSWORD": "admin",
    "BRIDGE_SYNC_CONTROL_TOKEN": "bridge_sync_control_dev",
    "ONLYOFFICE_JWT_SECRET": "onlyoffice_dev_secret",
}


def read_env_file(path: pathlib.Path):
    values = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def effective_value(key: str, env_values: dict):
    if key in os.environ and str(os.environ[key]).strip():
        return os.environ[key].strip()
    if key in env_values and str(env_values[key]).strip():
        return env_values[key].strip()
    return DEFAULTS.get(key, "")


def is_local_value(value: str):
    lowered = value.lower()
    return any(marker in lowered for marker in ("localhost", "127.0.0.1", "host.docker.internal"))


def main():
    env_values = read_env_file(ENV_FILE)

    checks = []
    blockers = []
    warnings = []

    env_present = ENV_FILE.exists()
    checks.append(
        {
            "name": "env_file",
            "status": "ok" if env_present else "warning",
            "details": str(ENV_FILE) if env_present else ".env not found; defaults/demo values may still be active",
        }
    )
    if not env_present:
        warnings.append("Не найден .env файл с production-настройками.")

    for key in ("GATEWAY_SERVER_NAME", "GATEWAY_TLS_CN", "RUKOVODITEL_PUBLIC_URL", "NAUDOC_PUBLIC_URL", "ONLYOFFICE_PUBLIC_JS_API_URL"):
        value = effective_value(key, env_values)
        local = is_local_value(value)
        checks.append(
            {
                "name": key,
                "status": "ok" if not local else "blocker",
                "details": value,
            }
        )
        if local:
            blockers.append(f"{key} still points to local/demo value: {value}")

    for key in ("RUKOVODITEL_DB_PASSWORD", "RUKOVODITEL_DB_ROOT_PASSWORD", "NAUDOC_PASSWORD", "BRIDGE_SYNC_CONTROL_TOKEN", "ONLYOFFICE_JWT_SECRET"):
        value = effective_value(key, env_values)
        default = DEFAULTS.get(key, "")
        unsafe = value == default or value.startswith("CHANGE_ME") or not value
        checks.append(
            {
                "name": key,
                "status": "ok" if not unsafe else "blocker",
                "details": "configured" if value else "empty",
            }
        )
        if unsafe:
            blockers.append(f"{key} is still default/unsafe.")

    for relative_path in ("ops/backup_all.sh", "ops/restore_all.sh", "ops/run_full_verification.sh"):
        path = ROOT_DIR / relative_path
        present = path.exists()
        checks.append(
            {
                "name": f"file:{relative_path}",
                "status": "ok" if present else "blocker",
                "details": str(path),
            }
        )
        if not present:
            blockers.append(f"Missing required ops file: {relative_path}")

    staging_path = ROOT_DIR / "docs" / "archive" / "SERVER_PREDEPLOY_CHECKLIST.md"
    checks.append(
        {
            "name": "staging_plan",
            "status": "ok" if staging_path.exists() else "warning",
            "details": str(staging_path),
        }
    )
    if not staging_path.exists():
        warnings.append("Не найден staging-checklist.")

    result = {
        "status": "ready" if not blockers else "not_ready",
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if blockers:
        print("\n[prod-audit] blocking issues found", file=sys.stderr)
        return 1

    print("\n[prod-audit] production baseline checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
