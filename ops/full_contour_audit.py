#!/usr/bin/env python3
import base64
import html
import http.cookiejar
import json
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from runtime_config import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    APP_CONTAINER,
    BRIDGE_BASE,
    DB_CONTAINER,
    EMPLOYEE_USERNAME,
    GATEWAY_BASE,
    MANAGER_USERNAME,
    NAUDOC_BASE,
    NAUDOC_LEGACY_CONTAINER,
    NAUDOC_PASSWORD,
    NAUDOC_USERNAME,
    NURSE_USERNAME,
    OFFICE_USERNAME,
    LOCAL_PROBE_IP,
    PUBLIC_NETLOC,
    REQUESTER_USERNAME,
    ROOT_DIR,
    ROLE_DEFAULT_PASSWORD,
    RUKOVODITEL_ENTRY,
)
SSL_CONTEXT = ssl._create_unverified_context()


def build_probe_request(url, data=None, headers=None):
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.hostname or not LOCAL_PROBE_IP:
        request = urllib.request.Request(url, data=data)
    else:
        netloc = LOCAL_PROBE_IP
        if parsed.port:
            netloc = f"{LOCAL_PROBE_IP}:{parsed.port}"

        probe_url = urllib.parse.urlunparse(
            (
                parsed.scheme,
                netloc,
                parsed.path or "/",
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )
        request = urllib.request.Request(probe_url, data=data)
        request.add_header("Host", parsed.netloc)

    for name, value in (headers or {}).items():
        request.add_header(name, value)

    return request


class LocalProbeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        data = req.data if code in (307, 308) else None
        redirected = build_probe_request(newurl, data=data)
        for name, value in req.header_items():
            if name.lower() == "host":
                continue
            if name.lower() == "content-length" and data is None:
                continue
            redirected.add_header(name, value)
        return redirected


def build_audit_opener(cookie_jar=None):
    handlers = [
        urllib.request.HTTPSHandler(context=SSL_CONTEXT),
        LocalProbeRedirectHandler(),
    ]
    if cookie_jar is not None:
        handlers.append(urllib.request.HTTPCookieProcessor(cookie_jar))
    return urllib.request.build_opener(*handlers)

ROLE_USERS = {
    "admin": {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "expected": ["Главная", "Работа", "Документы", "Контроль", "Канцелярия"],
        "unexpected": [],
        "extra_urls": [
            f"{GATEWAY_BASE}/index.php?module=configuration/application",
            f"{GATEWAY_BASE}/index.php?module=entities/entities",
            f"{GATEWAY_BASE}/index.php?module=users_groups/users_groups",
            f"{GATEWAY_BASE}/index.php?module=tools/db_backup",
            f"{GATEWAY_BASE}/index.php?module=logs/settings",
        ],
    },
    "manager": {
        "username": MANAGER_USERNAME,
        "password": ROLE_DEFAULT_PASSWORD,
        "expected": ["Главная", "Работа", "Документы", "Контроль"],
        "unexpected": ["Канцелярия"],
        "extra_urls": [],
    },
    "employee": {
        "username": EMPLOYEE_USERNAME,
        "password": ROLE_DEFAULT_PASSWORD,
        "expected": ["Главная", "Работа", "Документы"],
        "unexpected": ["Контроль", "Канцелярия"],
        "extra_urls": [],
    },
    "requester": {
        "username": REQUESTER_USERNAME,
        "password": ROLE_DEFAULT_PASSWORD,
        "expected": ["Главная", "Работа", "Документы"],
        "unexpected": ["Контроль", "Канцелярия"],
        "extra_urls": [],
    },
    "office": {
        "username": OFFICE_USERNAME,
        "password": ROLE_DEFAULT_PASSWORD,
        "expected": ["Главная", "Работа", "Документы", "Канцелярия"],
        "unexpected": ["Контроль"],
        "extra_urls": [],
    },
    "nurse": {
        "username": NURSE_USERNAME,
        "password": ROLE_DEFAULT_PASSWORD,
        "expected": ["Главная", "Работа", "Документы"],
        "unexpected": ["Контроль", "Канцелярия"],
        "extra_urls": [],
    },
}

SAFE_RUKOVODITEL_MODULE_PREFIXES = (
    "dashboard/",
    "dashboard/dashboard",
    "items/items",
    "reports/view",
    "users/account",
    "users/change_password",
    "configuration/application",
    "entities/entities",
    "users_groups/users_groups",
    "tools/db_backup",
    "logs/settings",
)

NAUDOC_SEED_PATHS = [
    "/docs/",
    "/docs/home",
    "/docs/inFrame?link=member_tasks",
    "/docs/inFrame?link=member_mail",
    "/docs/inFrame?link=member_documents",
    "/docs/inFrame?link=member_favorites",
    "/docs/inFrame?link=accessible_documents",
    "/docs/storage/view",
]

NAUDOC_ALLOWED_PATTERNS = (
    "/docs/home",
    "/docs/inFrame",
    "/docs/followup_in",
    "/docs/storage/view",
    "/docs/storage/members/",
    "/docs/storage/system/directories/",
    "/docs/storage/system/scripts/",
)

NAUDOC_BLOCK_PATTERNS = (
    "processFilterActions",
    "invoke_factory_form",
    "edit",
    "delete",
    "manage",
    "logout",
)


def run_cmd(args):
    completed = subprocess.run(
        args,
        cwd=ROOT_DIR,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def http_get(url, opener=None, headers=None):
    request = build_probe_request(url, headers=headers)

    if opener is None:
        opener = build_audit_opener()

    response = opener.open(request)
    body = response.read()
    return response, body


def decode_html(body, default="utf-8"):
    for encoding in ("utf-8", "cp1251", default):
        try:
            return body.decode(encoding)
        except UnicodeDecodeError:
            continue
    return body.decode(default, "ignore")


def parse_login_token(html_text):
    match = re.search(r'name="form_session_token" id="form_session_token" value="([^"]+)"', html_text)
    if not match:
        raise RuntimeError("Rukovoditel login token not found")
    return match.group(1)


def login_rukovoditel(username, password):
    cookie_jar = http.cookiejar.CookieJar()
    opener = build_audit_opener(cookie_jar)
    _, login_page = http_get(RUKOVODITEL_ENTRY, opener=opener)
    token = parse_login_token(decode_html(login_page))
    payload = urllib.parse.urlencode(
        {
            "form_session_token": token,
            "username": username,
            "password": password,
        }
    ).encode()
    response = opener.open(
        build_probe_request(
            f"{GATEWAY_BASE}/index.php?module=users/login&action=login",
            data=payload,
        )
    )
    body = decode_html(response.read())
    if "name=\"form_session_token\"" in body and "users/login" in response.geturl():
        raise RuntimeError(f"Login failed for {username}")
    return opener, response.geturl(), body


def extract_module_links(page_html):
    links = {}
    for href, text in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', page_html, re.S):
        clean_text = html.unescape(re.sub(r"<.*?>", "", text).strip())
        if not clean_text:
            continue
        absolute = urllib.parse.urljoin(GATEWAY_BASE + "/", html.unescape(href))
        parsed = urllib.parse.urlparse(absolute)
        if parsed.netloc != PUBLIC_NETLOC:
            continue
        module = urllib.parse.parse_qs(parsed.query).get("module", [""])[0]
        if module.startswith(SAFE_RUKOVODITEL_MODULE_PREFIXES):
            links[clean_text] = absolute
    return links


def check_rukovoditel_role(name, config):
    opener, final_url, body = login_rukovoditel(config["username"], config["password"])
    errors = []

    for label in config["expected"]:
        if label not in body:
            errors.append(f"missing menu label: {label}")
    for label in config["unexpected"]:
        if label in body:
            errors.append(f"unexpected menu label present: {label}")

    safe_links = extract_module_links(body)
    audit_urls = list(dict.fromkeys(list(safe_links.values()) + config["extra_urls"]))
    visited = []

    for url in audit_urls:
        response, page = http_get(url, opener=opener)
        page_html = decode_html(page)
        if response.geturl().startswith(f"{GATEWAY_BASE}/index.php?module=users/login"):
            errors.append(f"redirected to login from {url}")
            continue
        if "У вас нет доступа" in page_html or "Доступ запрещен" in page_html:
            errors.append(f"access denied on {url}")
            continue
        visited.append(url)

    return {
        "final_url": final_url,
        "menu_labels": sorted(safe_links.keys()),
        "visited_urls": visited,
        "errors": errors,
    }


def normalize_naudoc_path(href, current_url):
    absolute = urllib.parse.urljoin(current_url, href)
    parsed = urllib.parse.urlparse(absolute)
    if parsed.netloc != PUBLIC_NETLOC:
        return None
    if not parsed.path.startswith("/docs"):
        return None

    url = urllib.parse.urlunparse(("", "", parsed.path, "", parsed.query, ""))
    if any(pattern in url for pattern in NAUDOC_BLOCK_PATTERNS):
        return None
    if not any(url.startswith(pattern) for pattern in NAUDOC_ALLOWED_PATTERNS):
        return None
    return url


def check_naudoc():
    auth_header = {
        "Authorization": "Basic " + base64.b64encode(f"{NAUDOC_USERNAME}:{NAUDOC_PASSWORD}".encode()).decode(),
    }
    to_visit = list(NAUDOC_SEED_PATHS)
    seen = []
    seen_set = set()
    errors = []

    while to_visit and len(seen) < 20:
        path = to_visit.pop(0)
        if path in seen_set:
            continue
        seen_set.add(path)
        url = f"{GATEWAY_BASE}{path}"
        try:
            response, body = http_get(url, headers=auth_header)
            text = decode_html(body, default="cp1251")
        except urllib.error.HTTPError as exc:
            errors.append(f"http {exc.code} for {path}")
            continue
        except urllib.error.URLError as exc:
            errors.append(f"url error for {path}: {exc.reason}")
            continue

        if response.status != 200:
            errors.append(f"unexpected status {response.status} for {path}")
            continue
        if "host.docker.internal" in text or f"http://{PUBLIC_NETLOC}/docs" in text:
            errors.append(f"internal or insecure docs url leak in {path}")
        if "404" in text[:600] and "NauDoc" not in text:
            errors.append(f"page looks broken for {path}")

        discovered = []
        for href in re.findall(r'<a[^>]+href="([^"]+)"', text):
            normalized = normalize_naudoc_path(href, url)
            if normalized and normalized not in seen_set and normalized not in to_visit:
                to_visit.append(normalized)
                discovered.append(normalized)

        seen.append(
            {
                "path": path,
                "links_found": len(discovered),
            }
        )

    return {"visited": seen, "errors": errors}


def check_naudoc_addons():
    errors = []
    addon_log = run_cmd(
        [
            "docker",
            "exec",
            NAUDOC_LEGACY_CONTAINER,
            "bash",
            "-lc",
            "tail -n 400 /opt/naudoc/log/event.log | grep -n 'Bad magic number\\|Cannot import module\\|Could not import class' || true",
        ]
    )

    if "Bad magic number" in addon_log:
        errors.append("legacy add-ons are not loading because of bad magic number in compiled add-on packages")

    auth_header = {
        "Authorization": "Basic " + base64.b64encode(f"{NAUDOC_USERNAME}:{NAUDOC_PASSWORD}".encode()).decode(),
    }

    for path in [
        "/docs/directory_object.gif",
        "/docs/storage/system/directories/staff_list_directory/inFrame?link=view",
        "/docs/storage/system/directories/employee_list_directory/inFrame?link=view",
        "/docs/storage/system/directories/department_list_directory/inFrame?link=view",
        "/docs/storage/system/directories/post_list_directory/inFrame?link=view",
    ]:
        try:
            response, body = http_get(f"{GATEWAY_BASE}{path}", headers=auth_header)
            text = decode_html(body, default="cp1251")
            if response.status != 200:
                errors.append(f"unexpected status {response.status} for {path}")
            elif "broken" in text.lower():
                errors.append(f"broken object rendered for {path}")
        except urllib.error.HTTPError as exc:
            errors.append(f"http {exc.code} for {path}")
        except urllib.error.URLError as exc:
            errors.append(f"url error for {path}: {exc.reason}")

    return {"errors": errors}


def check_bridge():
    response, body = http_get(f"{BRIDGE_BASE}/health")
    health = json.loads(body.decode("utf-8"))
    links_response, links_body = http_get(f"{BRIDGE_BASE}/links")
    links = json.loads(links_body.decode("utf-8"))

    errors = []
    if response.status != 200 or health.get("status") != "ok":
        errors.append("bridge health is not ok")
    if links_response.status != 200:
        errors.append("bridge links endpoint is not available")
    for link in links:
        naudoc_url = link.get("naudoc_url", "")
        if naudoc_url and not naudoc_url.startswith(NAUDOC_BASE):
            errors.append(f"non-public naudoc url in bridge link #{link.get('id')}: {naudoc_url}")

    return {
        "links_total": len(links),
        "errors": errors,
    }


def run_sync_cycle():
    outputs = {}
    outputs["check_stack"] = run_cmd(["bash", "ops/check_stack.sh"])
    outputs["provision_test_users"] = run_cmd(["bash", "rukovoditel-test/provision_test_users.sh"])
    outputs["sync_requests"] = run_cmd(["bash", "rukovoditel-test/sync_service_requests.sh"])
    outputs["sync_projects"] = run_cmd(["bash", "rukovoditel-test/sync_project_documents.sh"])
    outputs["pull_bridge"] = run_cmd(["bash", "rukovoditel-test/pull_bridge_updates.sh", "--only-linked"])
    return outputs


def main():
    print("[audit] starting full contour audit")
    outputs = run_sync_cycle()
    print("[audit] sync cycle complete")

    results = {
        "stack": outputs,
        "roles": {},
        "naudoc": {},
        "bridge": {},
        "failures": [],
    }

    for name, config in ROLE_USERS.items():
        role_result = check_rukovoditel_role(name, config)
        results["roles"][name] = role_result
        results["failures"].extend([f"role:{name}: {item}" for item in role_result["errors"]])

    naudoc_result = check_naudoc()
    results["naudoc"] = naudoc_result
    results["failures"].extend([f"naudoc: {item}" for item in naudoc_result["errors"]])

    naudoc_addons_result = check_naudoc_addons()
    results["naudoc_addons"] = naudoc_addons_result
    results["failures"].extend([f"naudoc_addons: {item}" for item in naudoc_addons_result["errors"]])

    bridge_result = check_bridge()
    results["bridge"] = bridge_result
    results["failures"].extend([f"bridge: {item}" for item in bridge_result["errors"]])

    print(json.dumps(results, ensure_ascii=False, indent=2))

    if results["failures"]:
        print("[audit] failures detected", file=sys.stderr)
        return 1

    print("[audit] full contour is healthy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
