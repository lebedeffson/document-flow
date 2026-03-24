#!/usr/bin/env python3
import base64
import ssl
import urllib.error
import urllib.parse
import urllib.request


GATEWAY_BASE = "https://localhost:18443"
NAUDOC_BASE = f"{GATEWAY_BASE}/docs"
SSL_CONTEXT = ssl._create_unverified_context()
AUTH_HEADER = {
    "Authorization": "Basic " + base64.b64encode(b"admin:admin").decode(),
}
SMOKE_DOC_ID = "digital-signature-smoke"
SMOKE_DOC_TITLE = "Digital Signature Smoke"


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
    if code == 200 and 'value="DigitalSignature"' in addons_html and "Активен" in addons_html:
        checks.append("DigitalSignature add-on active")
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
