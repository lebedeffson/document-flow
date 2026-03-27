#!/usr/bin/env python3
import os
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


GATEWAY_BASE = _strip(os.environ.get('DOCFLOW_PUBLIC_BASE') or os.environ.get('RUKOVODITEL_PUBLIC_URL', 'https://localhost:18443'))
NAUDOC_BASE = _strip(os.environ.get('DOCFLOW_DOCS_BASE') or os.environ.get('NAUDOC_PUBLIC_URL', f'{GATEWAY_BASE}/docs'))
BRIDGE_BASE = _strip(os.environ.get('DOCFLOW_BRIDGE_PUBLIC_BASE') or f'{GATEWAY_BASE}/bridge')
OFFICE_BASE = _strip(os.environ.get('DOCFLOW_OFFICE_PUBLIC_BASE') or f'{GATEWAY_BASE}/office')
HTTP_BASE = _strip(os.environ.get('DOCFLOW_HTTP_BASE') or 'http://localhost:18090')

RUKOVODITEL_ENTRY = f'{GATEWAY_BASE}/index.php?module=dashboard/'
RUKOVODITEL_DIRECT = _strip(
    _normalize_host_runtime_url(os.environ.get('RUKOVODITEL_BASE_URL', 'http://localhost:18081'))
)

PUBLIC_NETLOC = urlparse(GATEWAY_BASE).netloc
DOCS_NETLOC = urlparse(NAUDOC_BASE).netloc

NAUDOC_USERNAME = os.environ.get('NAUDOC_USERNAME', 'admin')
NAUDOC_PASSWORD = os.environ.get('NAUDOC_PASSWORD', 'admin')

APP_CONTAINER = os.environ.get('RUKOVODITEL_CONTAINER_NAME', 'rukovoditel_test')
DB_CONTAINER = os.environ.get('RUKOVODITEL_DB_CONTAINER', 'rukovoditel_db_test')
ONLYOFFICE_CONTAINER = os.environ.get('ONLYOFFICE_CONTAINER_NAME', 'onlyoffice_docs_test')
NAUDOC_LEGACY_CONTAINER = os.environ.get('NAUDOC_LEGACY_CONTAINER', 'naudoc34_legacy')

DB_NAME = os.environ.get('RUKOVODITEL_DB_NAME', 'rukovoditel')
DB_USER = os.environ.get('RUKOVODITEL_DB_USER', 'rukovoditel')
DB_PASS = os.environ.get('RUKOVODITEL_DB_PASSWORD', 'rukovoditel')
JWT_SECRET = os.environ.get('ONLYOFFICE_JWT_SECRET', 'onlyoffice_dev_secret')
