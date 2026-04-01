#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

from runtime_config import DB_CONTAINER, DB_NAME, DB_PASS, DB_USER, NAUDOC_BASE, ROOT_DIR


BRIDGE_CONTAINER = os.environ.get("BRIDGE_CONTAINER", "docflow_bridge")


CORE_ENTITIES = {
    21: "Проекты и инициативы",
    22: "Поручения и задачи",
    23: "Заявки на обслуживание",
    24: "Рабочие обсуждения",
    25: "Карточки документов",
    26: "База документов",
    27: "Заявки на МТЗ",
}

EXPECTED_FIELDS = {
    21: ["Название проекта", "Ссылка на NauDoc", "Связанная карточка документа"],
    23: ["Тема заявки", "Связанная карточка документа", "Ссылка на NauDoc"],
    25: ["Наименование документа", "Ссылка на NauDoc", "Маршрут документа", "Совместное редактирование"],
    26: ["Название материала", "Ссылка на NauDoc"],
    27: ["Наименование потребности", "Связанный проект", "Ссылка на NauDoc"],
}


def run(args):
    return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', check=False)


def sql_quote(value: str) -> str:
    return value.replace("'", "''")


def run_mariadb_sql(sql: str):
    result = run(
        [
            "docker",
            "exec",
            "-e",
            f"MYSQL_PWD={DB_PASS}",
            DB_CONTAINER,
            "mariadb",
            "-u" + DB_USER,
            DB_NAME,
            "-N",
            "-e",
            sql,
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "mariadb query failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def run_bridge_python(code: str):
    result = run(["docker", "exec", BRIDGE_CONTAINER, "python", "-c", code])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "bridge sqlite query failed")
    return result.stdout.strip()


def single_int(sql: str) -> int:
    rows = run_mariadb_sql(sql)
    return int(rows[0]) if rows else 0


def collect_findings():
    findings = []
    notes = []

    # Core entity existence.
    entity_rows = run_mariadb_sql(
        "select id, name from app_entities where id in (21,22,23,24,25,26,27) order by id"
    )
    present_entities = {}
    for row in entity_rows:
        entity_id_str, entity_name = row.split("\t", 1)
        present_entities[int(entity_id_str)] = entity_name

    for entity_id, entity_name in CORE_ENTITIES.items():
        if entity_id not in present_entities:
            findings.append(f"Отсутствует сущность #{entity_id} `{entity_name}` в `app_entities`.")

    # Expected field presence.
    for entity_id, field_names in EXPECTED_FIELDS.items():
        for field_name in field_names:
            count = single_int(
                "select count(*) from app_fields "
                f"where entities_id={entity_id} and name='{sql_quote(field_name)}'"
            )
            if count == 0:
                findings.append(
                    f"В сущности #{entity_id} `{CORE_ENTITIES.get(entity_id, entity_id)}` "
                    f"не найдено поле `{field_name}`."
                )

    # Relational consistency in Rukovoditel.
    consistency_checks = [
        (
            "Ссылки заявок на карточки документов указывают на несуществующие документы.",
            "select count(*) from app_entity_23 r "
            "left join app_entity_25 d on cast(r.field_240 as unsigned)=d.id "
            "where trim(r.field_240)<>'' and d.id is null",
        ),
        (
            "Ссылки проектов на карточки документов указывают на несуществующие документы.",
            "select count(*) from app_entity_21 p "
            "left join app_entity_25 d on cast(p.field_279 as unsigned)=d.id "
            "where trim(p.field_279)<>'' and d.id is null",
        ),
        (
            "Карточки документов ссылаются на несуществующие заявки.",
            "select count(*) from app_entity_25 d "
            "left join app_entity_23 r on cast(d.field_252 as unsigned)=r.id "
            "where trim(d.field_252)<>'' and r.id is null",
        ),
        (
            "Карточки документов ссылаются на несуществующие проекты.",
            "select count(*) from app_entity_25 d "
            "left join app_entity_21 p on cast(d.field_251 as unsigned)=p.id "
            "where trim(d.field_251)<>'' and p.id is null",
        ),
        (
            "Заявки и карточки документов имеют несогласованные перекрестные связи.",
            "select count(*) from app_entity_23 r "
            "join app_entity_25 d on cast(r.field_240 as unsigned)=d.id "
            "where trim(r.field_240)<>'' and cast(d.field_252 as unsigned)<>r.id",
        ),
        (
            "Проекты и карточки документов имеют несогласованные перекрестные связи.",
            "select count(*) from app_entity_21 p "
            "join app_entity_25 d on cast(p.field_279 as unsigned)=d.id "
            "where trim(p.field_279)<>'' and cast(d.field_251 as unsigned)<>p.id",
        ),
        (
            "Одна и та же карточка документа привязана к нескольким заявкам.",
            "select count(*) from ("
            "select trim(field_240) doc_id, count(*) c "
            "from app_entity_23 where trim(field_240)<>'' group by trim(field_240) having count(*)>1"
            ") x",
        ),
        (
            "Одна и та же карточка документа привязана к нескольким проектам.",
            "select count(*) from ("
            "select trim(field_279) doc_id, count(*) c "
            "from app_entity_21 where trim(field_279)<>'' group by trim(field_279) having count(*)>1"
            ") x",
        ),
        (
            "Есть карточки документов без маршрута документа.",
            "select count(*) from app_entity_25 where field_294=0 or trim(field_294)=''",
        ),
    ]

    for message, sql in consistency_checks:
        count = single_int(sql)
        if count > 0:
            findings.append(f"{message} Найдено: {count}.")

    doc_total = single_int("select count(*) from app_entity_25")
    naudoc_storage_prefix = sql_quote(NAUDOC_BASE.rstrip("/") + "/storage/")
    docs_with_specific_naudoc = single_int(
        "select count(*) from app_entity_25 "
        f"where trim(field_250)<>'' and field_250 like '{naudoc_storage_prefix}%'"
    )
    notes.append(
        f"Карточек документов: {doc_total}, с конкретной ссылкой NauDoc: {docs_with_specific_naudoc}."
    )

    # Bridge checks.
    bridge_info = json.loads(
        run_bridge_python(
            r"""
import json, sqlite3
conn = sqlite3.connect("/data/bridge.db")
cur = conn.cursor()
tables = [row[0] for row in cur.execute("select name from sqlite_master where type='table'").fetchall()]
payload = {"tables": tables, "counts": {}, "open_sync_failures": 0}
for table in [
    "document_links",
    "sync_failures",
    "sync_status_mappings",
    "sync_field_mappings",
    "user_directory_profiles",
    "identity_sources",
    "hospital_role_mappings",
    "document_route_definitions",
]:
    if table in tables:
        payload["counts"][table] = cur.execute(f"select count(*) from {table}").fetchone()[0]
payload["open_sync_failures"] = cur.execute(
    "select count(*) from sync_failures where status <> 'resolved'"
).fetchone()[0]
print(json.dumps(payload, ensure_ascii=False))
"""
        )
    )

    required_bridge_tables = [
        "document_links",
        "sync_failures",
        "sync_status_mappings",
        "sync_field_mappings",
        "user_directory_profiles",
        "identity_sources",
        "hospital_role_mappings",
        "document_route_definitions",
    ]
    for table in required_bridge_tables:
        if table not in bridge_info["tables"]:
            findings.append(f"В Bridge отсутствует таблица `{table}`.")

    if bridge_info["open_sync_failures"] > 0:
        findings.append(
            f"В Bridge есть незакрытые sync failures: {bridge_info['open_sync_failures']}."
        )

    route_def_count = bridge_info["counts"].get("document_route_definitions", 0)
    if route_def_count < 8:
        findings.append(
            f"В Bridge недостаточно hospital-маршрутов: найдено {route_def_count}, ожидается минимум 8."
        )

    notes.append(
        "Bridge counts: "
        + ", ".join(
            f"{name}={count}" for name, count in sorted(bridge_info["counts"].items())
        )
    )

    return findings, notes


def main():
    try:
        findings, notes = collect_findings()
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    status = "ok" if not findings else "issues"
    print(json.dumps({"status": status, "findings": findings, "notes": notes}, ensure_ascii=False, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
