#!/usr/bin/env python3
import http.cookiejar
import json
import re
import ssl
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
GATEWAY_BASE = 'https://localhost:18443'
RUKOVODITEL_DIRECT = 'http://localhost:18081'
SSL_CONTEXT = ssl._create_unverified_context()
SEED_SCRIPT = ROOT_DIR / 'rukovoditel-test' / 'seed_onlyoffice_pilot.sh'
APP_CONTAINER = 'rukovoditel_test'
DB_CONTAINER = 'rukovoditel_db_test'
DB_NAME = 'rukovoditel'
DB_USER = 'rukovoditel'
DB_PASS = 'rukovoditel'
JWT_SECRET = 'onlyoffice_dev_secret'


def run_cmd(args):
    return subprocess.check_output(args, cwd=ROOT_DIR, text=True).strip()


def seed_pilot():
    output = run_cmd([str(SEED_SCRIPT)])
    data = {}
    for line in output.splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            data[key.strip()] = value.strip()
    return data


def db_value(sql):
    return run_cmd([
        'docker', 'exec', DB_CONTAINER, 'mariadb', '-N', '-s',
        f'-u{DB_USER}', f'-p{DB_PASS}', DB_NAME, '-e', sql,
    ])


def build_opener():
    cookie_jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=SSL_CONTEXT),
        urllib.request.HTTPCookieProcessor(cookie_jar),
    )


def login(user_agent):
    opener = build_opener()
    req = urllib.request.Request(f'{GATEWAY_BASE}/', headers={'User-Agent': user_agent})
    body = opener.open(req).read().decode('utf-8', 'ignore')
    token = re.search(r'name="form_session_token" id="form_session_token" value="([^"]+)"', body)
    if not token:
        raise RuntimeError('login token not found')
    payload = urllib.parse.urlencode({
        'form_session_token': token.group(1),
        'username': 'admin',
        'password': 'admin123',
    }).encode()
    opener.open(urllib.request.Request(
        f'{GATEWAY_BASE}/index.php?module=users/login&action=login',
        data=payload,
        headers={'User-Agent': user_agent},
    ))
    return opener, token.group(1)


def fetch_editor_html(user_agent, item_id, field_id, file_id):
    opener, token = login(user_agent)
    editor_url = (
        f'{GATEWAY_BASE}/index.php?module=items/onlyoffice_editor'
        f'&path=25-{item_id}&action=open&field={field_id}&file={file_id}'
        f'&token={urllib.parse.quote(token)}'
    )
    html = opener.open(urllib.request.Request(editor_url, headers={'User-Agent': user_agent})).read().decode('utf-8', 'ignore')
    return html


def parse_value(html, pattern, label):
    match = re.search(pattern, html)
    if not match:
        raise RuntimeError(f'{label} not found in editor config')
    return match.group(1)


def assert_pk_header(url):
    cmd = [
        'docker', 'exec', 'onlyoffice_docs_test', 'sh', '-lc',
        f"curl -s '{url}' | od -An -tx1 -N4",
    ]
    magic = run_cmd(cmd).strip()
    if magic != '50 4b 03 04':
        raise RuntimeError(f'unexpected document magic bytes: {magic}')
    return magic


def generate_callback_jwt():
    php = (
        'require "/var/www/html/includes/libs/jwt/JWT.php"; '
        f'echo Firebase\\JWT\\JWT::encode(["status"=>4], "{JWT_SECRET}", "HS256");'
    )
    return run_cmd(['docker', 'exec', APP_CONTAINER, 'php', '-r', php])


def post_callback(item_id, field_id, file_id, date_added):
    token = generate_callback_jwt()
    url = (
        f'{RUKOVODITEL_DIRECT}/index.php?module=onlyoffice/callback'
        f'&entity_id=25&item_id={item_id}&field={field_id}&file={file_id}&date={date_added}'
    )
    req = urllib.request.Request(
        url,
        data=json.dumps({'token': token}).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(req) as response:
        body = json.loads(response.read().decode('utf-8', 'ignore'))
    if body.get('error') != 0:
        raise RuntimeError(f'callback failed: {body}')
    return body


def main():
    seed = seed_pilot()
    item_id = int(seed['item_id'])
    field_id = int(seed['field_id'])
    file_id = int(seed['file_id'])
    row = db_value(f"select date_added from app_onlyoffice_files where id={file_id};")
    date_added = int(row)

    health = urllib.request.urlopen(urllib.request.Request(f'{GATEWAY_BASE}/office/healthcheck'), context=SSL_CONTEXT).read().decode()
    if health.strip().lower() != 'true':
        raise RuntimeError(f'ONLYOFFICE healthcheck failed: {health}')

    desktop_html = fetch_editor_html(
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123 Safari/537.36',
        item_id,
        field_id,
        file_id,
    )
    mobile_html = fetch_editor_html(
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1',
        item_id,
        field_id,
        file_id,
    )

    desktop_type = parse_value(desktop_html, r'"type":"(desktop|mobile)"', 'desktop type')
    mobile_type = parse_value(mobile_html, r'"type":"(desktop|mobile)"', 'mobile type')
    callback_url = parse_value(desktop_html, r'"callbackUrl":"([^"]+)"', 'callbackUrl').replace('\\/', '/')
    download_url = parse_value(desktop_html, r'"url":"([^"]+module=onlyoffice\\/download[^"]+)"', 'downloadUrl').replace('\\/', '/')

    if desktop_type != 'desktop':
        raise RuntimeError(f'unexpected desktop editor type: {desktop_type}')
    if mobile_type != 'mobile':
        raise RuntimeError(f'unexpected mobile editor type: {mobile_type}')
    if not callback_url.startswith('http://rukovoditel/'):
        raise RuntimeError(f'callbackUrl is not internal: {callback_url}')
    if not download_url.startswith('http://rukovoditel/'):
        raise RuntimeError(f'downloadUrl is not internal: {download_url}')

    magic = assert_pk_header(download_url)
    callback_result = post_callback(item_id, field_id, file_id, date_added)
    cleared_token = db_value(f"select download_token from app_onlyoffice_files where id={file_id};")
    if cleared_token:
        raise RuntimeError('download token was not cleared after callback status=4')

    refreshed_html = fetch_editor_html(
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123 Safari/537.36',
        item_id,
        field_id,
        file_id,
    )
    refreshed_download_url = parse_value(refreshed_html, r'"url":"([^"]+module=onlyoffice\\/download[^"]+)"', 'refreshed downloadUrl').replace('\\/', '/')
    refreshed_token = urllib.parse.parse_qs(urllib.parse.urlparse(refreshed_download_url).query).get('token', [''])[0]
    if not refreshed_token:
        raise RuntimeError('download token was not regenerated after reopening editor')

    report = {
        'seed': seed,
        'desktop_type': desktop_type,
        'mobile_type': mobile_type,
        'callback_url': callback_url,
        'download_url': download_url,
        'download_magic': magic,
        'callback_result': callback_result,
        'refreshed_download_token': refreshed_token,
        'status': 'ok',
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'ONLYOFFICE audit failed: {exc}', file=sys.stderr)
        sys.exit(1)
