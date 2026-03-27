#!/usr/bin/env python3
import base64
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request

from runtime_config import NAUDOC_BASE, NAUDOC_USERNAME, NAUDOC_PASSWORD


SSL_CONTEXT = ssl._create_unverified_context()
AUTH_HEADER = {
    "Authorization": "Basic " + base64.b64encode(f"{NAUDOC_USERNAME}:{NAUDOC_PASSWORD}".encode()).decode(),
}
SMOKE_DOC_ID = "digital-signature-smoke"
SMOKE_DOC_TITLE = "Digital Signature Smoke"
REQUIRE_DIGITAL_SIGNATURE = os.environ.get("DOCFLOW_REQUIRE_DIGITAL_SIGNATURE", "").lower() in {"1", "true", "yes"}


def http_open(url, data=None, headers=None):
    request = urllib.request.Request(url, data=data)
    merged_headers = {}
    merged_headers.update(AUTH_HEADER)
    merged_headers.update(headers or {})
    for name, value in merged_headers.items():
        request.add_header(name, value)
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=SSL_CONTEXT))
    return opener.open(request)


def fetch_text(url):
    response = http_open(url)
    body = response.read()
    for encoding in ("utf-8", "cp1251", "windows-1251"):
        try:
            return response.getcode(), body.decode(encoding)
        except UnicodeDecodeError:
            continue
    return response.getcode(), body.decode("utf-8", "ignore")


def ensure_smoke_document():
    smoke_form_url = f"{NAUDOC_BASE}/storage/members/admin/{SMOKE_DOC_ID}/document_signatures_form"
    try:
        code, text = fetch_text(smoke_form_url)
        if code == 200 and "CAPICOM.SignedData" in text:
            return SMOKE_DOC_ID, False
    except urllib.error.HTTPError:
        pass

    payload = urllib.parse.urlencode(
        {
            "type_name": "HTMLDocument",
            "id:id_": SMOKE_DOC_ID,
            "title:required:string": SMOKE_DOC_TITLE,
            "description:text": "Digital signature smoke test document",
            "cat_id": "Document",
            "create": "Применить",
        }
    ).encode()
    http_open(
        f"{NAUDOC_BASE}/storage/members/admin/invoke_factory",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).read()
    return SMOKE_DOC_ID, True


def main():
    checks = []
    errors = []

    code, addons_html = fetch_text(f"{NAUDOC_BASE}/manage_addons_form")
    addon_marker = 'value="DigitalSignature"'
    addon_index = addons_html.find(addon_marker)
    addon_window = ""
    if addon_index != -1:
        addon_window = addons_html[max(0, addon_index - 80): addon_index + 300]

    if code == 200 and addon_index != -1 and "Активен" in addon_window:
        checks.append("DigitalSignature add-on active")
    elif code == 200 and addon_index != -1 and "Отключен" in addon_window:
        message = "DigitalSignature add-on is installed but disabled"
        if REQUIRE_DIGITAL_SIGNATURE:
            errors.append(message)
        else:
            print(f"[ds-audit] skipped: {message}")
            return
    else:
        errors.append("DigitalSignature add-on is not active in manage_addons_form")

    code, manage_html = fetch_text(f"{NAUDOC_BASE}/manage_signature_form")
    if code == 200 and "CEnroll.CEnroll.1" in manage_html and "xEnroll" in manage_html:
        checks.append("DigitalSignature admin settings page available")
    else:
        errors.append("manage_signature_form is unavailable or missing xEnroll controls")

    code, personalize_html = fetch_text(f"{NAUDOC_BASE}/personalize_form")
    if code == 200 and 'name="ds_certificate"' in personalize_html and "CAPICOM.Store" in personalize_html:
        checks.append("Personal certificate selection available")
    else:
        errors.append("personalize_form does not expose ds_certificate selection")

    doc_id, created = ensure_smoke_document()
    code, inframe_html = fetch_text(f"{NAUDOC_BASE}/storage/members/admin/{doc_id}/inFrame?link=view")
    if code == 200 and "document_signatures_form" in inframe_html and "Подписи" in inframe_html:
        checks.append("HTMLDocument shows signatures tab")
    else:
        errors.append("HTMLDocument does not expose signatures tab")

    code, signatures_html = fetch_text(f"{NAUDOC_BASE}/storage/members/admin/{doc_id}/document_signatures_form")
    if code == 200 and "CAPICOM.SignedData" in signatures_html and "Подписать" in signatures_html:
        checks.append("Document signatures form available")
    else:
        errors.append("document_signatures_form is unavailable or incomplete")

    print("[ds-audit] checks:")
    for item in checks:
        print(f"  - {item}")
    print(f"[ds-audit] smoke document: {doc_id} ({'created' if created else 'reused'})")

    if errors:
        print("[ds-audit] errors:")
        for item in errors:
            print(f"  - {item}")
        raise SystemExit(1)

    print("[ds-audit] contour is healthy")


if __name__ == "__main__":
    main()
