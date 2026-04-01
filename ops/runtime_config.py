#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
from urllib.parse import urlparse, urlunparse


ROOT_DIR = Path(__file__).resolve().parent.parent


def _load_env_defaults():
    env_file = Path(os.environ.get("DOCFLOW_ENV_FILE", ROOT_DIR / ".env"))
    if not env_file.is_file():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


_load_env_defaults()


def _strip(value: str) -> str:
    return value.rstrip('/')


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def _bool_env(name: str, default: str = "0") -> bool:
    return _env(name, default).strip().lower() in ("1", "true", "yes", "on")


def _normalize_host_runtime_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.hostname != "host.docker.internal":
        return value

    netloc = "localhost"
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"

    return urlunparse(
        (
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )


def _looks_like_wsl_bash(path: str) -> bool:
    normalized = path.replace("/", "\\").lower()
    return normalized.endswith("\\windows\\system32\\bash.exe")


def _find_bash_bin() -> str:
    if os.name != "nt":
        return shutil.which("bash") or "bash"

    candidates = [
        Path(r"C:\Program Files\Git\bin\bash.exe"),
        Path(r"C:\Program Files\Git\usr\bin\bash.exe"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    discovered = shutil.which("bash")
    if discovered and not _looks_like_wsl_bash(discovered):
        return discovered

    return "bash"


def bash_script_command(script_path, *args) -> list[str]:
    path = Path(script_path)
    return [BASH_BIN, path.as_posix(), *(str(arg) for arg in args)]


GATEWAY_BASE = _strip(os.environ.get('DOCFLOW_PUBLIC_BASE') or os.environ.get('RUKOVODITEL_PUBLIC_URL', 'https://localhost:18443'))
NAUDOC_BASE = _strip(os.environ.get('DOCFLOW_DOCS_BASE') or os.environ.get('NAUDOC_PUBLIC_URL', f'{GATEWAY_BASE}/docs'))
BRIDGE_BASE = _strip(os.environ.get('DOCFLOW_BRIDGE_PUBLIC_BASE') or f'{GATEWAY_BASE}/bridge')
DOCSPACE_BASE = _strip(os.environ.get('DOCFLOW_DOCSPACE_PUBLIC_BASE') or os.environ.get('DOCSPACE_PUBLIC_URL', f'{GATEWAY_BASE}/docspace'))
WORKSPACE_BASE = _strip(os.environ.get('DOCFLOW_WORKSPACE_PUBLIC_BASE') or os.environ.get('WORKSPACE_PUBLIC_URL', f'{GATEWAY_BASE}/workspace'))
OFFICE_BASE = _strip(os.environ.get('DOCFLOW_OFFICE_PUBLIC_BASE') or f'{GATEWAY_BASE}/office')
HTTP_BASE = _strip(os.environ.get('DOCFLOW_HTTP_BASE') or 'http://localhost:18090')
DOCSPACE_ENABLED = _bool_env('DOCSPACE_ENABLED', '1')
WORKSPACE_ENABLED = _bool_env('WORKSPACE_ENABLED', '1')
DOCSPACE_TARGET_URL = _strip(_env('DOCSPACE_TARGET_URL')) if _env('DOCSPACE_TARGET_URL') else ''
WORKSPACE_TARGET_URL = _strip(_env('WORKSPACE_TARGET_URL')) if _env('WORKSPACE_TARGET_URL') else ''
LOCAL_PROBE_IP = _env('DOCFLOW_LOCAL_PROBE_IP', '127.0.0.1')

RUKOVODITEL_ENTRY = f'{GATEWAY_BASE}/index.php?module=dashboard/'
RUKOVODITEL_DIRECT = _strip(
    _normalize_host_runtime_url(os.environ.get('RUKOVODITEL_BASE_URL', 'http://localhost:18081'))
)

PUBLIC_NETLOC = urlparse(GATEWAY_BASE).netloc
DOCS_NETLOC = urlparse(NAUDOC_BASE).netloc
BASH_BIN = _find_bash_bin()

NAUDOC_USERNAME = os.environ.get('NAUDOC_USERNAME', 'admin')
NAUDOC_PASSWORD = os.environ.get('NAUDOC_PASSWORD', 'admin')
SHOW_DEMO_LOGIN_MODES = _bool_env('DOCFLOW_SHOW_DEMO_LOGIN_MODES', '0')
ADMIN_USERNAME = _env('DOCFLOW_ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = _env('DOCFLOW_ADMIN_PASSWORD', 'admin123')
OFFICE_ADMIN_EMAIL = _env('DOCFLOW_OFFICE_ADMIN_EMAIL', 'admin@hospital.local')
OFFICE_ADMIN_PASSWORD = _env('DOCFLOW_OFFICE_ADMIN_PASSWORD', 'Admin2026!')
ROLE_DEFAULT_PASSWORD = _env('DOCFLOW_ROLE_DEFAULT_PASSWORD', 'rolepass123')
MANAGER_USERNAME = _env('DOCFLOW_MANAGER_USERNAME', 'department.head')
EMPLOYEE_USERNAME = _env('DOCFLOW_EMPLOYEE_USERNAME', 'clinician.primary')
REQUESTER_USERNAME = _env('DOCFLOW_REQUESTER_USERNAME', 'registry.operator')
OFFICE_USERNAME = _env('DOCFLOW_OFFICE_USERNAME', 'records.office')
NURSE_USERNAME = _env('DOCFLOW_NURSE_USERNAME', 'nurse.coordinator')

APP_CONTAINER = os.environ.get('RUKOVODITEL_CONTAINER_NAME', 'rukovoditel_test')
DB_CONTAINER = os.environ.get('RUKOVODITEL_DB_CONTAINER', 'rukovoditel_db_test')
ONLYOFFICE_CONTAINER = os.environ.get('ONLYOFFICE_CONTAINER_NAME', 'onlyoffice_docs_test')
NAUDOC_LEGACY_CONTAINER = os.environ.get('NAUDOC_LEGACY_CONTAINER', 'naudoc34_legacy')

DB_NAME = os.environ.get('RUKOVODITEL_DB_NAME', 'rukovoditel')
DB_USER = os.environ.get('RUKOVODITEL_DB_USER', 'rukovoditel')
DB_PASS = os.environ.get('RUKOVODITEL_DB_PASSWORD', 'rukovoditel')
JWT_SECRET = os.environ.get('ONLYOFFICE_JWT_SECRET', 'onlyoffice_dev_secret')
