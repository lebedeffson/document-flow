import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, redirect, render_template, request, url_for
from werkzeug.middleware.proxy_fix import ProxyFix


APP_TITLE = "NauDoc Bridge"
DB_PATH = os.environ.get("BRIDGE_DB_PATH", "/data/bridge.db")
NAUDOC_BASE_URL = os.environ.get("NAUDOC_BASE_URL", "http://host.docker.internal:18080/docs")
NAUDOC_PUBLIC_URL = os.environ.get("NAUDOC_PUBLIC_URL", NAUDOC_BASE_URL)
NAUDOC_USERNAME = os.environ.get("NAUDOC_USERNAME", "admin")
NAUDOC_PASSWORD = os.environ.get("NAUDOC_PASSWORD", "admin")
RUKOVODITEL_BASE_URL = os.environ.get("RUKOVODITEL_BASE_URL", "http://host.docker.internal:18081")
RUKOVODITEL_PUBLIC_URL = os.environ.get("RUKOVODITEL_PUBLIC_URL", RUKOVODITEL_BASE_URL)
REQUEST_TIMEOUT = float(os.environ.get("BRIDGE_REQUEST_TIMEOUT", "8"))

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


def utcnow_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS document_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_system TEXT NOT NULL,
                external_entity TEXT NOT NULL,
                external_item_id TEXT NOT NULL,
                external_title TEXT NOT NULL,
                naudoc_url TEXT NOT NULL,
                naudoc_title TEXT NOT NULL,
                sync_status TEXT NOT NULL DEFAULT 'linked',
                notes TEXT NOT NULL DEFAULT '',
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_document_links_external
            ON document_links (external_system, external_entity, external_item_id)
            """
        )
        conn.commit()


def db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row):
    item = dict(row)
    item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
    return item


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def normalize_naudoc_url(value):
    url = normalize_text(value)
    if not url:
        return ""

    known_bases = [
        NAUDOC_PUBLIC_URL.rstrip("/"),
        NAUDOC_BASE_URL.rstrip("/"),
        "http://localhost:18080/docs",
        "http://host.docker.internal:18080/docs",
        "https://localhost:18443/docs",
    ]

    for base in dict.fromkeys(filter(None, known_bases)):
        if url.startswith(base):
            return NAUDOC_PUBLIC_URL.rstrip("/") + url[len(base):]

    return url


def fetch_nau_doc_status():
    try:
        response = requests.get(
            NAUDOC_BASE_URL,
            auth=(NAUDOC_USERNAME, NAUDOC_PASSWORD),
            timeout=REQUEST_TIMEOUT,
        )
        return {
            "ok": response.ok,
            "status_code": response.status_code,
            "url": NAUDOC_BASE_URL,
            "title_hint": "NauDoc" if "NauDoc" in response.text or "docs" in response.url else "",
        }
    except requests.RequestException as exc:
        return {
            "ok": False,
            "status_code": None,
            "url": NAUDOC_BASE_URL,
            "error": str(exc),
        }


def fetch_rukovoditel_status():
    try:
        response = requests.get(
            RUKOVODITEL_BASE_URL,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,
        )
        location = response.headers.get("Location", "")
        return {
            "ok": response.status_code in (200, 301, 302),
            "status_code": response.status_code,
            "url": RUKOVODITEL_BASE_URL,
            "redirect": location,
        }
    except requests.RequestException as exc:
        return {
            "ok": False,
            "status_code": None,
            "url": RUKOVODITEL_BASE_URL,
            "error": str(exc),
        }


def validate_payload(payload):
    required = [
        "external_system",
        "external_entity",
        "external_item_id",
        "external_title",
    ]
    missing = [name for name in required if not str(payload.get(name, "")).strip()]
    if missing:
        return False, {"error": "Missing required fields", "fields": missing}
    return True, None


def parse_payload():
    payload = request.get_json(silent=True)
    if payload is None:
        payload = request.form.to_dict(flat=True)
        if "metadata_json" in request.form:
            metadata_json = request.form.get("metadata_json", "").strip() or "{}"
            try:
                payload["metadata"] = json.loads(metadata_json)
            except json.JSONDecodeError:
                return None, (jsonify({"error": "metadata_json must be valid JSON"}), 400)

    if not isinstance(payload, dict):
        return None, (jsonify({"error": "Payload must be an object"}), 400)

    return payload, None


def prepare_link_row(payload):
    metadata = payload.get("metadata") or {}
    now = utcnow_iso()
    naudoc_url = normalize_naudoc_url(payload.get("naudoc_url"))
    naudoc_title = normalize_text(payload.get("naudoc_title")) or normalize_text(payload.get("external_title"))
    sync_status = normalize_text(payload.get("sync_status"))
    if not sync_status:
        sync_status = "linked" if naudoc_url else "pending_nau_doc"

    row = (
        normalize_text(payload["external_system"]),
        normalize_text(payload["external_entity"]),
        normalize_text(payload["external_item_id"]),
        normalize_text(payload["external_title"]),
        naudoc_url,
        naudoc_title,
        sync_status,
        normalize_text(payload.get("notes")),
        json.dumps(metadata, ensure_ascii=False, sort_keys=True),
        now,
        now,
    )
    return row


def build_updates_from_payload(existing, payload):
    metadata = payload.get("metadata")
    updates = {
        "external_title": normalize_text(payload.get("external_title")) or existing["external_title"],
        "naudoc_url": normalize_naudoc_url(payload.get("naudoc_url")) if "naudoc_url" in payload else existing["naudoc_url"],
        "naudoc_title": normalize_text(payload.get("naudoc_title")) if "naudoc_title" in payload else existing["naudoc_title"],
        "sync_status": normalize_text(payload.get("sync_status")) or existing["sync_status"],
        "notes": normalize_text(payload.get("notes")) if "notes" in payload else existing["notes"],
    }
    if metadata is None:
        metadata_json = existing["metadata_json"]
    else:
        metadata_json = json.dumps(metadata, ensure_ascii=False, sort_keys=True)
    return updates, metadata_json


def get_link_by_external_key(conn, external_system, external_entity, external_item_id):
    return conn.execute(
        """
        SELECT *
        FROM document_links
        WHERE external_system = ? AND external_entity = ? AND external_item_id = ?
        """,
        (external_system, external_entity, external_item_id),
    ).fetchone()


def apply_link_filters(sql, values, args):
    external_system = normalize_text(args.get("external_system"))
    external_entity = normalize_text(args.get("external_entity"))
    external_item_id = normalize_text(args.get("external_item_id"))
    sync_status = normalize_text(args.get("sync_status"))
    view = normalize_text(args.get("view"))

    where = []
    if external_system:
        where.append("external_system = ?")
        values.append(external_system)
    if external_entity:
        where.append("external_entity = ?")
        values.append(external_entity)
    if external_item_id:
        where.append("external_item_id = ?")
        values.append(external_item_id)
    if sync_status:
        where.append("sync_status = ?")
        values.append(sync_status)
    elif view == "pending":
        where.append("sync_status LIKE ?")
        values.append("pending%")
    elif view == "problem":
        where.append("(sync_status LIKE ? OR lower(sync_status) LIKE ? OR lower(sync_status) LIKE ?)")
        values.extend(["pending%", "%error%", "%fail%"])
    elif view == "signed":
        where.append("sync_status = ?")
        values.append("signed")
    elif view == "linked":
        where.append("sync_status = ?")
        values.append("linked")

    if where:
        sql += " WHERE " + " AND ".join(where)
    return sql, values, {
        "external_system": external_system,
        "external_entity": external_entity,
        "external_item_id": external_item_id,
        "sync_status": sync_status,
        "view": view or "all",
    }


def fetch_summary_counts(conn):
    return conn.execute(
        """
        SELECT
            COUNT(*) AS total_count,
            SUM(CASE WHEN sync_status LIKE 'pending%' THEN 1 ELSE 0 END) AS pending_count,
            SUM(CASE WHEN lower(sync_status) LIKE '%error%' OR lower(sync_status) LIKE '%fail%' THEN 1 ELSE 0 END) AS error_count,
            SUM(CASE WHEN sync_status = 'signed' THEN 1 ELSE 0 END) AS signed_count,
            SUM(CASE
                WHEN sync_status LIKE 'pending%'
                  OR lower(sync_status) LIKE '%error%'
                  OR lower(sync_status) LIKE '%fail%'
                THEN 1 ELSE 0 END
            ) AS attention_count
        FROM document_links
        """
    ).fetchone()


@app.before_request
def _ensure_db_ready():
    ensure_db()


@app.get("/")
def index():
    with closing(db_connection()) as conn:
        sql = """
            SELECT *
            FROM document_links
        """
        sql, values, selected_filters = apply_link_filters(sql, [], request.args)
        rows = conn.execute(sql + " ORDER BY updated_at DESC, id DESC", values).fetchall()
        summary = fetch_summary_counts(conn)
        attention_rows = conn.execute(
            """
            SELECT *
            FROM document_links
            WHERE sync_status LIKE 'pending%'
               OR lower(sync_status) LIKE '%error%'
               OR lower(sync_status) LIKE '%fail%'
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()
    return render_template(
        "index.html",
        app_title=APP_TITLE,
        naudoc_url=NAUDOC_PUBLIC_URL,
        rukovoditel_url=RUKOVODITEL_PUBLIC_URL,
        links=[row_to_dict(row) for row in rows],
        attention_links=[row_to_dict(row) for row in attention_rows],
        selected_filters=selected_filters,
        summary_counts=dict(summary),
    )


@app.get("/health")
def health():
    with closing(db_connection()) as conn:
        total_links = conn.execute("SELECT COUNT(*) AS cnt FROM document_links").fetchone()["cnt"]
    return jsonify(
        {
            "service": APP_TITLE,
            "status": "ok",
            "checked_at": utcnow_iso(),
            "links_total": total_links,
            "systems": {
                "naudoc": fetch_nau_doc_status(),
                "rukovoditel": fetch_rukovoditel_status(),
            },
        }
    )


@app.get("/links")
def list_links():
    sql = """
        SELECT *
        FROM document_links
    """
    sql, values, _ = apply_link_filters(sql, [], request.args)
    sql += " ORDER BY updated_at DESC, id DESC"

    with closing(db_connection()) as conn:
        rows = conn.execute(sql, values).fetchall()
    return jsonify([row_to_dict(row) for row in rows])


@app.get("/links/lookup")
def lookup_link():
    external_system = normalize_text(request.args.get("external_system"))
    external_entity = normalize_text(request.args.get("external_entity"))
    external_item_id = normalize_text(request.args.get("external_item_id"))

    if not (external_system and external_entity and external_item_id):
        return (
            jsonify(
                {
                    "error": "external_system, external_entity and external_item_id are required",
                }
            ),
            400,
        )

    with closing(db_connection()) as conn:
        row = get_link_by_external_key(conn, external_system, external_entity, external_item_id)
    if row is None:
        return jsonify({"error": "Link not found"}), 404
    return jsonify(row_to_dict(row))


@app.get("/links/<int:link_id>")
def get_link(link_id):
    with closing(db_connection()) as conn:
        row = conn.execute("SELECT * FROM document_links WHERE id = ?", (link_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Link not found"}), 404
    return jsonify(row_to_dict(row))


@app.post("/links")
def create_link():
    payload, error_response = parse_payload()
    if error_response:
        return error_response

    valid, error = validate_payload(payload)
    if not valid:
        return jsonify(error), 400

    row = prepare_link_row(payload)

    try:
        with closing(db_connection()) as conn:
            cursor = conn.execute(
                """
                INSERT INTO document_links (
                    external_system,
                    external_entity,
                    external_item_id,
                    external_title,
                    naudoc_url,
                    naudoc_title,
                    sync_status,
                    notes,
                    metadata_json,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                row,
            )
            conn.commit()
            new_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return (
            jsonify(
                {
                    "error": "Link for this external record already exists",
                    "external_system": normalize_text(payload["external_system"]),
                    "external_entity": normalize_text(payload["external_entity"]),
                    "external_item_id": normalize_text(payload["external_item_id"]),
                }
            ),
            409,
        )

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "created", "id": new_id}), 201


@app.post("/links/upsert")
def upsert_link():
    payload, error_response = parse_payload()
    if error_response:
        return error_response

    valid, error = validate_payload(payload)
    if not valid:
        return jsonify(error), 400

    external_system = normalize_text(payload["external_system"])
    external_entity = normalize_text(payload["external_entity"])
    external_item_id = normalize_text(payload["external_item_id"])

    with closing(db_connection()) as conn:
        existing = get_link_by_external_key(conn, external_system, external_entity, external_item_id)
        if existing is None:
            row = prepare_link_row(payload)
            cursor = conn.execute(
                """
                INSERT INTO document_links (
                    external_system,
                    external_entity,
                    external_item_id,
                    external_title,
                    naudoc_url,
                    naudoc_title,
                    sync_status,
                    notes,
                    metadata_json,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                row,
            )
            conn.commit()
            row = conn.execute("SELECT * FROM document_links WHERE id = ?", (cursor.lastrowid,)).fetchone()
            return jsonify({"status": "created", "link": row_to_dict(row)}), 201

        updates, metadata_json = build_updates_from_payload(existing, payload)

        conn.execute(
            """
            UPDATE document_links
            SET external_title = ?,
                naudoc_url = ?,
                naudoc_title = ?,
                sync_status = ?,
                notes = ?,
                metadata_json = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                updates["external_title"],
                updates["naudoc_url"],
                updates["naudoc_title"],
                updates["sync_status"],
                updates["notes"],
                metadata_json,
                utcnow_iso(),
                existing["id"],
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM document_links WHERE id = ?", (existing["id"],)).fetchone()
    return jsonify({"status": "updated", "link": row_to_dict(row)})


@app.post("/links/<int:link_id>/update")
def update_link_form(link_id):
    payload, error_response = parse_payload()
    if error_response:
        return error_response

    with closing(db_connection()) as conn:
        existing = conn.execute("SELECT * FROM document_links WHERE id = ?", (link_id,)).fetchone()
        if existing is None:
            return jsonify({"error": "Link not found"}), 404

        updates, metadata_json = build_updates_from_payload(existing, payload)
        conn.execute(
            """
            UPDATE document_links
            SET external_title = ?,
                naudoc_url = ?,
                naudoc_title = ?,
                sync_status = ?,
                notes = ?,
                metadata_json = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                updates["external_title"],
                updates["naudoc_url"],
                updates["naudoc_title"],
                updates["sync_status"],
                updates["notes"],
                metadata_json,
                utcnow_iso(),
                link_id,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM document_links WHERE id = ?", (link_id,)).fetchone()

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "updated", "link": row_to_dict(row)})


@app.patch("/links/<int:link_id>")
@app.put("/links/<int:link_id>")
def update_link(link_id):
    payload = request.get_json(silent=True) or {}
    allowed = {"sync_status", "notes", "naudoc_url", "naudoc_title", "external_title", "metadata"}
    updates = {key: value for key, value in payload.items() if key in allowed}
    if not updates:
        return jsonify({"error": "No updatable fields provided"}), 400

    clauses = []
    values = []
    if "metadata" in updates:
        clauses.append("metadata_json = ?")
        values.append(json.dumps(updates.pop("metadata"), ensure_ascii=False, sort_keys=True))
    for key, value in updates.items():
        clauses.append(f"{key} = ?")
        values.append(str(value))
    clauses.append("updated_at = ?")
    values.append(utcnow_iso())
    values.append(link_id)

    with closing(db_connection()) as conn:
        cursor = conn.execute(
            f"UPDATE document_links SET {', '.join(clauses)} WHERE id = ?",
            values,
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Link not found"}), 404
        row = conn.execute("SELECT * FROM document_links WHERE id = ?", (link_id,)).fetchone()
    return jsonify(row_to_dict(row))


@app.delete("/links/<int:link_id>")
def delete_link(link_id):
    with closing(db_connection()) as conn:
        cursor = conn.execute("DELETE FROM document_links WHERE id = ?", (link_id,))
        conn.commit()
    if cursor.rowcount == 0:
        return jsonify({"error": "Link not found"}), 404
    return jsonify({"status": "deleted", "id": link_id})


if __name__ == "__main__":
    ensure_db()
    app.run(host="0.0.0.0", port=8000, debug=False)
