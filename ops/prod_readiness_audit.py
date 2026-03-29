#!/usr/bin/env python3
import json
import os
import pathlib
import sys
from urllib.parse import urlparse


ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
ENV_FILE = pathlib.Path(os.environ.get("DOCFLOW_ENV_FILE", str(ROOT_DIR / ".env")))
PREFER_ENV_FILE = "DOCFLOW_ENV_FILE" in os.environ


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
    "LDAP_ADMIN_PASSWORD": "ldap_admin_dev",
    "LDAP_CONFIG_PASSWORD": "ldap_config_dev",
    "LDAP_BIND_PASSWORD": "ldap_bind_dev",
    "DOCFLOW_ADMIN_PASSWORD": "admin123",
    "DOCFLOW_ROLE_DEFAULT_PASSWORD": "rolepass123",
    "DOCFLOW_MANAGER_USERNAME": "department.head",
    "DOCFLOW_EMPLOYEE_USERNAME": "clinician.primary",
    "DOCFLOW_REQUESTER_USERNAME": "registry.operator",
    "DOCFLOW_OFFICE_USERNAME": "records.office",
    "DOCFLOW_NURSE_USERNAME": "nurse.coordinator",
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
    if PREFER_ENV_FILE and key in env_values and str(env_values[key]).strip():
        return env_values[key].strip()
    if key in os.environ and str(os.environ[key]).strip():
        return os.environ[key].strip()
    if key in env_values and str(env_values[key]).strip():
        return env_values[key].strip()
    return DEFAULTS.get(key, "")


def is_local_value(value: str):
    lowered = value.lower()
    return any(marker in lowered for marker in ("localhost", "127.0.0.1", "host.docker.internal"))


def is_unusable_proxy_target(value: str):
    try:
        parsed = urlparse(value.strip())
    except Exception:
        return True

    hostname = (parsed.hostname or "").strip().lower()
    return hostname in ("", "localhost") or hostname.startswith("127.")


def is_truthy(value: str):
    return value.strip().lower() in ("1", "true", "yes", "on")


def looks_like_http_url(value: str):
    lowered = value.strip().lower()
    return lowered.startswith("http://") or lowered.startswith("https://")


def looks_like_demo_username(value: str):
    lowered = value.strip().lower()
    if not lowered:
        return True

    return any(marker in lowered for marker in ("demo", ".test", "test.", "_test"))


def check_optional_target_url(env_values: dict, checks: list, blockers: list, key: str):
    value = effective_value(key, env_values)
    if not value:
        return

    invalid = not looks_like_http_url(value)
    unusable = is_unusable_proxy_target(value) if not invalid else False
    checks.append(
        {
            "name": key,
            "status": "ok" if not (invalid or unusable) else "blocker",
            "details": value,
        }
    )
    if invalid:
        blockers.append(f"{key} is not a valid http(s) URL: {value}")
    if unusable:
        blockers.append(f"{key} points to an unusable loopback target for gateway proxying: {value}")


def main():
    env_values = read_env_file(ENV_FILE)

    checks = []
    blockers = []
    warnings = []
    require_live_targets = is_truthy(effective_value("DOCFLOW_OFFICE_WAVE1_REQUIRE_LIVE_TARGETS", env_values) or "0")

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

    for key in (
        "RUKOVODITEL_DB_PASSWORD",
        "RUKOVODITEL_DB_ROOT_PASSWORD",
        "NAUDOC_PASSWORD",
        "BRIDGE_SYNC_CONTROL_TOKEN",
        "ONLYOFFICE_JWT_SECRET",
        "LDAP_ADMIN_PASSWORD",
        "LDAP_CONFIG_PASSWORD",
        "LDAP_BIND_PASSWORD",
        "DOCFLOW_ADMIN_PASSWORD",
        "DOCFLOW_ROLE_DEFAULT_PASSWORD",
    ):
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

    demo_login_modes = effective_value("DOCFLOW_SHOW_DEMO_LOGIN_MODES", env_values) or "0"
    checks.append(
        {
            "name": "DOCFLOW_SHOW_DEMO_LOGIN_MODES",
            "status": "ok" if not is_truthy(demo_login_modes) else "blocker",
            "details": demo_login_modes,
        }
    )
    if is_truthy(demo_login_modes):
        blockers.append("DOCFLOW_SHOW_DEMO_LOGIN_MODES is enabled; demo credentials are visible on the login page.")

    for key in (
        "DOCFLOW_MANAGER_USERNAME",
        "DOCFLOW_EMPLOYEE_USERNAME",
        "DOCFLOW_REQUESTER_USERNAME",
        "DOCFLOW_OFFICE_USERNAME",
        "DOCFLOW_NURSE_USERNAME",
    ):
        value = effective_value(key, env_values)
        demo_like = looks_like_demo_username(value)
        checks.append(
            {
                "name": key,
                "status": "ok" if not demo_like else "blocker",
                "details": value or "empty",
            }
        )
        if demo_like:
            blockers.append(f"{key} still uses demo/test semantics: {value or 'empty'}")

    for service_name, enabled_key, public_key, target_key in (
        ("DocSpace", "DOCSPACE_ENABLED", "DOCSPACE_PUBLIC_URL", "DOCSPACE_TARGET_URL"),
        ("Workspace", "WORKSPACE_ENABLED", "WORKSPACE_PUBLIC_URL", "WORKSPACE_TARGET_URL"),
    ):
        enabled_value = effective_value(enabled_key, env_values) or "0"
        enabled = is_truthy(enabled_value)
        checks.append(
            {
                "name": enabled_key,
                "status": "ok" if enabled else "warning",
                "details": enabled_value,
            }
        )
        if not enabled:
            warnings.append(f"{service_name} disabled in env. Если сервис входит в первую волну, включите {enabled_key}=1.")
            continue

        public_url = effective_value(public_key, env_values)
        public_local = is_local_value(public_url) if public_url else False
        public_missing = not public_url
        checks.append(
            {
                "name": public_key,
                "status": "ok" if (public_url and not public_local) else ("warning" if public_missing else "blocker"),
                "details": public_url or "empty",
            }
        )
        if public_missing:
            warnings.append(f"{public_key} is empty. Runtime can derive it, but explicit value is preferred for release packaging.")
        elif public_local:
            blockers.append(f"{public_key} still points to local/demo value: {public_url}")

        target_url = effective_value(target_key, env_values)
        if not target_url:
            checks.append(
                {
                    "name": target_key,
                    "status": "blocker" if require_live_targets else "warning",
                    "details": "shell-only mode",
                }
            )
            if require_live_targets:
                blockers.append(f"{service_name} is required in live-target mode, but {target_key} is empty.")
            else:
                warnings.append(f"{service_name} runs in shell-only mode. Set {target_key} to route the live service through the gateway.")
            continue

        target_invalid = not looks_like_http_url(target_url)
        target_unusable = is_unusable_proxy_target(target_url) if not target_invalid else False
        checks.append(
            {
                "name": target_key,
                "status": "ok" if not (target_invalid or target_unusable) else "blocker",
                "details": target_url,
            }
        )
        if target_invalid:
            blockers.append(f"{target_key} is not a valid http(s) URL: {target_url}")
        if target_unusable:
            blockers.append(f"{target_key} points to an unusable loopback target for gateway proxying: {target_url}")

    for key in (
        "DOCSPACE_COLLABORATION_ROOM_TARGET_URL",
        "DOCSPACE_PUBLIC_ROOM_TARGET_URL",
        "DOCSPACE_FORM_FILLING_ROOM_TARGET_URL",
        "WORKSPACE_CALENDAR_TARGET_URL",
        "WORKSPACE_COMMUNITY_TARGET_URL",
    ):
        check_optional_target_url(env_values, checks, blockers, key)

    checks.append(
        {
            "name": "DOCFLOW_OFFICE_WAVE1_REQUIRE_LIVE_TARGETS",
            "status": "ok" if require_live_targets else "warning",
            "details": "1" if require_live_targets else "0",
        }
    )
    if not require_live_targets:
        warnings.append("Live-target enforcement for DocSpace/Workspace is disabled. Enable DOCFLOW_OFFICE_WAVE1_REQUIRE_LIVE_TARGETS=1 before final production cutover.")

    for relative_path in (
        "ops/backup_all.sh",
        "ops/restore_all.sh",
        "ops/run_full_verification.sh",
        "ops/generate_staging_env.sh",
        "ops/monitoring_snapshot.py",
        "ops/install_monitor_timer.sh",
        "ops/systemd/docflow-monitor.service",
        "ops/systemd/docflow-monitor.timer",
    ):
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

    staging_runbook = ROOT_DIR / "docs" / "reference" / "STAGING_RUNBOOK.md"
    checks.append(
        {
            "name": "staging_runbook",
            "status": "ok" if staging_runbook.exists() else "warning",
            "details": str(staging_runbook),
        }
    )
    if not staging_runbook.exists():
        warnings.append("Не найден staging runbook.")

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
