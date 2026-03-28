import json
import os
import re
import sqlite3
import ssl
import urllib.parse
from contextlib import closing
from datetime import datetime, timezone
from html import escape as html_escape

import requests
from flask import Flask, jsonify, redirect, render_template, request, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

try:
    from ldap3 import ALL_ATTRIBUTES, AUTO_BIND_NO_TLS, AUTO_BIND_TLS_BEFORE_BIND, Connection, Server, SUBTREE, Tls

    LDAP3_AVAILABLE = True
except ImportError:
    ALL_ATTRIBUTES = None
    AUTO_BIND_NO_TLS = None
    AUTO_BIND_TLS_BEFORE_BIND = None
    Connection = None
    Server = None
    SUBTREE = None
    Tls = None
    LDAP3_AVAILABLE = False


APP_TITLE = "NauDoc Bridge"
DB_PATH = os.environ.get("BRIDGE_DB_PATH", "/data/bridge.db")
NAUDOC_BASE_URL = os.environ.get("NAUDOC_BASE_URL", "http://host.docker.internal:18080/docs")
NAUDOC_PUBLIC_URL = os.environ.get("NAUDOC_PUBLIC_URL", NAUDOC_BASE_URL)
NAUDOC_USERNAME = os.environ.get("NAUDOC_USERNAME", "admin")
NAUDOC_PASSWORD = os.environ.get("NAUDOC_PASSWORD", "admin")
RUKOVODITEL_BASE_URL = os.environ.get("RUKOVODITEL_BASE_URL", "http://host.docker.internal:18081")
RUKOVODITEL_PUBLIC_URL = os.environ.get("RUKOVODITEL_PUBLIC_URL", RUKOVODITEL_BASE_URL)
SYNC_CONTROL_URL = os.environ.get("SYNC_CONTROL_URL", f"{RUKOVODITEL_BASE_URL.rstrip('/')}/run_sync_job.php")
SYNC_CONTROL_TOKEN = os.environ.get("SYNC_CONTROL_TOKEN", "")
REQUEST_TIMEOUT = float(os.environ.get("BRIDGE_REQUEST_TIMEOUT", "8"))
LDAP_REQUEST_TIMEOUT = max(int(REQUEST_TIMEOUT), 1)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

DEFAULT_STATUS_MAPPINGS = [
    {
        "sort_order": 10,
        "match_type": "contains",
        "match_value": "error",
        "request_status_name": "",
        "doc_status_name": "",
        "integration_status_name": "Ошибка синхронизации",
        "notes": "Техническая ошибка интеграции",
    },
    {
        "sort_order": 20,
        "match_type": "contains",
        "match_value": "ошиб",
        "request_status_name": "",
        "doc_status_name": "",
        "integration_status_name": "Ошибка синхронизации",
        "notes": "Русскоязычная ошибка интеграции",
    },
    {
        "sort_order": 30,
        "match_type": "contains",
        "match_value": "failed",
        "request_status_name": "",
        "doc_status_name": "",
        "integration_status_name": "Ошибка синхронизации",
        "notes": "Ошибка повторной обработки",
    },
    {
        "sort_order": 40,
        "match_type": "exact",
        "match_value": "pending_nau_doc",
        "request_status_name": "",
        "doc_status_name": "",
        "integration_status_name": "Ожидает документ",
        "notes": "Карточка создана, официальный документ еще не назначен",
    },
    {
        "sort_order": 50,
        "match_type": "contains",
        "match_value": "чернов",
        "request_status_name": "Новая",
        "doc_status_name": "Черновик",
        "integration_status_name": "Черновик",
        "notes": "Черновой этап",
    },
    {
        "sort_order": 60,
        "match_type": "contains",
        "match_value": "draft",
        "request_status_name": "Новая",
        "doc_status_name": "Черновик",
        "integration_status_name": "Черновик",
        "notes": "Черновой этап",
    },
    {
        "sort_order": 70,
        "match_type": "contains",
        "match_value": "отклон",
        "request_status_name": "Отклонена",
        "doc_status_name": "",
        "integration_status_name": "",
        "notes": "Документ или заявка отклонены",
    },
    {
        "sort_order": 80,
        "match_type": "contains",
        "match_value": "reject",
        "request_status_name": "Отклонена",
        "doc_status_name": "",
        "integration_status_name": "",
        "notes": "Документ или заявка отклонены",
    },
    {
        "sort_order": 90,
        "match_type": "contains",
        "match_value": "ожидает",
        "request_status_name": "Ожидает заявителя",
        "doc_status_name": "",
        "integration_status_name": "",
        "notes": "Ожидание ответа заявителя",
    },
    {
        "sort_order": 100,
        "match_type": "contains",
        "match_value": "waiting",
        "request_status_name": "Ожидает заявителя",
        "doc_status_name": "",
        "integration_status_name": "",
        "notes": "Ожидание ответа заявителя",
    },
    {
        "sort_order": 110,
        "match_type": "contains",
        "match_value": "архив",
        "request_status_name": "Выполнена",
        "doc_status_name": "Архивирован",
        "integration_status_name": "Архивирован",
        "notes": "Архивный документ",
    },
    {
        "sort_order": 120,
        "match_type": "contains",
        "match_value": "archive",
        "request_status_name": "Выполнена",
        "doc_status_name": "Архивирован",
        "integration_status_name": "Архивирован",
        "notes": "Архивный документ",
    },
    {
        "sort_order": 130,
        "match_type": "contains",
        "match_value": "ознаком",
        "request_status_name": "",
        "doc_status_name": "На ознакомлении",
        "integration_status_name": "На ознакомлении",
        "notes": "Ознакомление",
    },
    {
        "sort_order": 140,
        "match_type": "contains",
        "match_value": "familiar",
        "request_status_name": "",
        "doc_status_name": "На ознакомлении",
        "integration_status_name": "На ознакомлении",
        "notes": "Ознакомление",
    },
    {
        "sort_order": 150,
        "match_type": "contains",
        "match_value": "подпис",
        "request_status_name": "Выполнена",
        "doc_status_name": "Подписан",
        "integration_status_name": "Подписан",
        "notes": "Документ подписан",
    },
    {
        "sort_order": 160,
        "match_type": "contains",
        "match_value": "sign",
        "request_status_name": "Выполнена",
        "doc_status_name": "Подписан",
        "integration_status_name": "Подписан",
        "notes": "Документ подписан",
    },
    {
        "sort_order": 170,
        "match_type": "contains",
        "match_value": "утверж",
        "request_status_name": "На согласовании",
        "doc_status_name": "На утверждении",
        "integration_status_name": "На утверждении",
        "notes": "Документ на утверждении",
    },
    {
        "sort_order": 180,
        "match_type": "contains",
        "match_value": "approve",
        "request_status_name": "На согласовании",
        "doc_status_name": "На утверждении",
        "integration_status_name": "На утверждении",
        "notes": "Документ на утверждении",
    },
    {
        "sort_order": 190,
        "match_type": "exact",
        "match_value": "linked",
        "request_status_name": "На согласовании",
        "doc_status_name": "На согласовании",
        "integration_status_name": "Связано",
        "notes": "Связь создана и документ назначен",
    },
    {
        "sort_order": 200,
        "match_type": "contains",
        "match_value": "соглас",
        "request_status_name": "На согласовании",
        "doc_status_name": "На согласовании",
        "integration_status_name": "На согласовании",
        "notes": "Согласование",
    },
    {
        "sort_order": 210,
        "match_type": "contains",
        "match_value": "review",
        "request_status_name": "На согласовании",
        "doc_status_name": "На согласовании",
        "integration_status_name": "На согласовании",
        "notes": "Согласование",
    },
    {
        "sort_order": 220,
        "match_type": "contains",
        "match_value": "register",
        "request_status_name": "На согласовании",
        "doc_status_name": "На согласовании",
        "integration_status_name": "На согласовании",
        "notes": "Регистрация и согласование",
    },
]

DEFAULT_FIELD_MAPPINGS = [
    {
        "source_system": "rukovoditel",
        "source_entity": "service_requests",
        "source_field_key": "request_id",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "request_id",
        "direction": "push",
        "notes": "ID заявки в рабочем контуре",
        "is_required": 1,
        "sort_order": 10,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "service_requests",
        "source_field_key": "request_url",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "request_url",
        "direction": "push",
        "notes": "Публичная ссылка на заявку",
        "sort_order": 20,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "service_requests",
        "source_field_key": "doc_card_id",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "doc_card_id",
        "direction": "push",
        "notes": "Связанная карточка документа",
        "is_required": 1,
        "sort_order": 30,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "service_requests",
        "source_field_key": "doc_card_url",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "doc_card_url",
        "direction": "push",
        "notes": "Ссылка на карточку документа",
        "sort_order": 40,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "service_requests",
        "source_field_key": "document_route",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "document_route",
        "direction": "push",
        "notes": "Маршрут связанного документа по заявке",
        "sort_order": 45,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "service_requests",
        "source_field_key": "responsible_user_id",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "responsible_user_id",
        "direction": "push",
        "notes": "Ответственный пользователь по заявке",
        "sort_order": 50,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "service_requests",
        "source_field_key": "request_title",
        "target_system": "naudoc",
        "target_entity": "document",
        "target_field_key": "title",
        "direction": "push",
        "notes": "Проекция заголовка документа в NauDoc",
        "sort_order": 60,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "service_requests",
        "source_field_key": "request_url",
        "target_system": "naudoc",
        "target_entity": "document",
        "target_field_key": "source_request_url",
        "direction": "push",
        "notes": "Проекция ссылки на заявку в NauDoc",
        "sort_order": 70,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "service_requests",
        "source_field_key": "doc_card_url",
        "target_system": "naudoc",
        "target_entity": "document",
        "target_field_key": "source_doc_card_url",
        "direction": "push",
        "notes": "Проекция ссылки на карточку документа в NauDoc",
        "sort_order": 80,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "service_requests",
        "source_field_key": "document_route",
        "target_system": "naudoc",
        "target_entity": "workflow",
        "target_field_key": "route_label",
        "direction": "push",
        "notes": "Проекция hospital-маршрута документа в NauDoc",
        "sort_order": 90,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "projects",
        "source_field_key": "project_id",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "project_id",
        "direction": "push",
        "notes": "ID проекта",
        "is_required": 1,
        "sort_order": 110,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "projects",
        "source_field_key": "project_url",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "project_url",
        "direction": "push",
        "notes": "Публичная ссылка на проект",
        "sort_order": 120,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "projects",
        "source_field_key": "doc_card_id",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "doc_card_id",
        "direction": "push",
        "notes": "Связанная карточка проекта",
        "is_required": 1,
        "sort_order": 130,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "projects",
        "source_field_key": "doc_card_url",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "doc_card_url",
        "direction": "push",
        "notes": "Ссылка на карточку проекта",
        "sort_order": 140,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "projects",
        "source_field_key": "document_route",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "document_route",
        "direction": "push",
        "notes": "Маршрут связанного документа проекта",
        "sort_order": 145,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "projects",
        "source_field_key": "manager_user_id",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "manager_user_id",
        "direction": "push",
        "notes": "Ответственный руководитель проекта",
        "sort_order": 150,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "projects",
        "source_field_key": "project_title",
        "target_system": "naudoc",
        "target_entity": "document",
        "target_field_key": "title",
        "direction": "push",
        "notes": "Проекция заголовка документа проекта в NauDoc",
        "sort_order": 160,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "projects",
        "source_field_key": "project_url",
        "target_system": "naudoc",
        "target_entity": "document",
        "target_field_key": "source_project_url",
        "direction": "push",
        "notes": "Проекция ссылки на проект в NauDoc",
        "sort_order": 170,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "projects",
        "source_field_key": "doc_card_url",
        "target_system": "naudoc",
        "target_entity": "document",
        "target_field_key": "source_doc_card_url",
        "direction": "push",
        "notes": "Проекция ссылки на карточку проекта в NauDoc",
        "sort_order": 180,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "projects",
        "source_field_key": "document_route",
        "target_system": "naudoc",
        "target_entity": "workflow",
        "target_field_key": "route_label",
        "direction": "push",
        "notes": "Проекция hospital-маршрута документа проекта в NauDoc",
        "sort_order": 190,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "document_cards",
        "source_field_key": "doc_card_id",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "doc_card_id",
        "direction": "push",
        "notes": "ID карточки документа",
        "is_required": 1,
        "sort_order": 210,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "document_cards",
        "source_field_key": "doc_card_url",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "doc_card_url",
        "direction": "push",
        "notes": "Ссылка на карточку документа",
        "sort_order": 220,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "document_cards",
        "source_field_key": "source_request_id",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "source_request_id",
        "direction": "push",
        "notes": "Источник связи: заявка",
        "sort_order": 230,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "document_cards",
        "source_field_key": "source_request_url",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "source_request_url",
        "direction": "push",
        "notes": "Ссылка на заявку-источник",
        "sort_order": 240,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "document_cards",
        "source_field_key": "source_project_id",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "source_project_id",
        "direction": "push",
        "notes": "Источник связи: проект",
        "sort_order": 250,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "document_cards",
        "source_field_key": "source_project_url",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "source_project_url",
        "direction": "push",
        "notes": "Ссылка на проект-источник",
        "sort_order": 260,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "document_cards",
        "source_field_key": "document_route",
        "target_system": "bridge",
        "target_entity": "metadata",
        "target_field_key": "document_route",
        "direction": "push",
        "notes": "Маршрут документа из карточки",
        "sort_order": 265,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "document_cards",
        "source_field_key": "doc_card_title",
        "target_system": "naudoc",
        "target_entity": "document",
        "target_field_key": "title",
        "direction": "push",
        "notes": "Проекция заголовка карточки документа в NauDoc",
        "sort_order": 270,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "document_cards",
        "source_field_key": "doc_card_url",
        "target_system": "naudoc",
        "target_entity": "document",
        "target_field_key": "source_doc_card_url",
        "direction": "push",
        "notes": "Проекция ссылки на карточку документа в NauDoc",
        "sort_order": 280,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "document_cards",
        "source_field_key": "source_request_url",
        "target_system": "naudoc",
        "target_entity": "document",
        "target_field_key": "source_request_url",
        "direction": "push",
        "notes": "Проекция ссылки на исходную заявку в NauDoc",
        "sort_order": 290,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "document_cards",
        "source_field_key": "source_project_url",
        "target_system": "naudoc",
        "target_entity": "document",
        "target_field_key": "source_project_url",
        "direction": "push",
        "notes": "Проекция ссылки на исходный проект в NauDoc",
        "sort_order": 300,
    },
    {
        "source_system": "rukovoditel",
        "source_entity": "document_cards",
        "source_field_key": "document_route",
        "target_system": "naudoc",
        "target_entity": "workflow",
        "target_field_key": "route_label",
        "direction": "push",
        "notes": "Проекция маршрута документа в NauDoc",
        "sort_order": 310,
    },
]

DEFAULT_IDENTITY_SOURCES = [
    {
        "source_key": "rukovoditel_local",
        "source_label": "Локальный каталог Rukovoditel",
        "provider_type": "local",
        "source_system": "rukovoditel",
        "sync_mode": "pull",
        "host": "docflow_rukovoditel",
        "port": 80,
        "ssl_mode": "http",
        "base_dn": "",
        "user_base_dn": "",
        "group_base_dn": "",
        "login_attribute": "username",
        "display_name_attribute": "full_name",
        "email_attribute": "email",
        "department_attribute": "department",
        "role_attribute": "role",
        "bind_dn": "",
        "bind_password_env_key": "",
        "notes": "Основной рабочий каталог пользователей платформы.",
        "is_active": 1,
        "is_default": 1,
    },
    {
        "source_key": "naudoc_catalog",
        "source_label": "Каталог NauDoc",
        "provider_type": "external",
        "source_system": "naudoc",
        "sync_mode": "pull",
        "host": "docflow_zope",
        "port": 8080,
        "ssl_mode": "http",
        "base_dn": "",
        "user_base_dn": "/storage/members",
        "group_base_dn": "",
        "login_attribute": "member_id",
        "display_name_attribute": "title",
        "email_attribute": "email",
        "department_attribute": "department",
        "role_attribute": "role",
        "bind_dn": "",
        "bind_password_env_key": "",
        "notes": "Официальный каталог учетных записей документного контура.",
        "is_active": 1,
        "is_default": 0,
    },
    {
        "source_key": "hospital_ldap",
        "source_label": "Корпоративный LDAP/AD",
        "provider_type": "ldap",
        "source_system": "ldap",
        "sync_mode": "sso",
        "host": "ldap.hospital.local",
        "port": 636,
        "ssl_mode": "ldaps",
        "base_dn": "dc=hospital,dc=local",
        "user_base_dn": "ou=Users,dc=hospital,dc=local",
        "group_base_dn": "ou=Groups,dc=hospital,dc=local",
        "login_attribute": "sAMAccountName",
        "display_name_attribute": "displayName",
        "email_attribute": "mail",
        "department_attribute": "department",
        "role_attribute": "title",
        "bind_dn": "cn=svc-docflow,ou=Service Accounts,dc=hospital,dc=local",
        "bind_password_env_key": "LDAP_BIND_PASSWORD",
        "notes": "Целевой единый каталог пользователей для hospital production. Секреты хранятся в .env, а не в Bridge.",
        "is_active": 0,
        "is_default": 0,
    },
]

DEFAULT_HOSPITAL_ROLE_MAPPINGS = [
    {
        "source_system": "rukovoditel",
        "source_role_key": "admin",
        "source_role_label": "Администратор платформы",
        "hospital_role_key": "hospital_admin",
        "hospital_role_label": "ИТ-администратор / администратор платформы",
        "access_scope": "full",
        "notes": "Полный административный доступ к платформе и интеграциям.",
        "is_active": 1,
        "sort_order": 10,
    },
    {
        "source_system": "rukovoditel",
        "source_role_key": "manager",
        "source_role_label": "Заведующий отделением / руководитель подразделения",
        "hospital_role_key": "department_head",
        "hospital_role_label": "Заведующий отделением / руководитель подразделения",
        "access_scope": "department",
        "notes": "Управление документами и задачами своего подразделения.",
        "is_active": 1,
        "sort_order": 20,
    },
    {
        "source_system": "rukovoditel",
        "source_role_key": "employee",
        "source_role_label": "Врач / сотрудник подразделения",
        "hospital_role_key": "clinician",
        "hospital_role_label": "Врач / сотрудник подразделения",
        "access_scope": "own",
        "notes": "Работа со своими документами и доступными записями подразделения.",
        "is_active": 1,
        "sort_order": 30,
    },
    {
        "source_system": "rukovoditel",
        "source_role_key": "nurse_coordinator",
        "source_role_label": "Старшая медсестра / координатор отделения",
        "hospital_role_key": "nurse_coordinator",
        "hospital_role_label": "Старшая медсестра / координатор отделения",
        "access_scope": "department",
        "notes": "Координация маршрутов отделения, сопровождение документов и контроль исполнения на уровне поста/отделения.",
        "is_active": 1,
        "sort_order": 35,
    },
    {
        "source_system": "rukovoditel",
        "source_role_key": "requester",
        "source_role_label": "Регистратура / заявитель",
        "hospital_role_key": "registry_operator",
        "hospital_role_label": "Регистратура / заявитель",
        "access_scope": "registry",
        "notes": "Первичная регистрация и запуск маршрутов документов.",
        "is_active": 1,
        "sort_order": 40,
    },
    {
        "source_system": "rukovoditel",
        "source_role_key": "office",
        "source_role_label": "Канцелярия / делопроизводство",
        "hospital_role_key": "records_office",
        "hospital_role_label": "Канцелярия / делопроизводство",
        "access_scope": "office",
        "notes": "Официальная регистрация, контроль и архивный контур.",
        "is_active": 1,
        "sort_order": 50,
    },
    {
        "source_system": "ldap",
        "source_role_key": "",
        "source_role_label": "ИТ-администратор / администратор платформы",
        "hospital_role_key": "hospital_admin",
        "hospital_role_label": "ИТ-администратор / администратор платформы",
        "access_scope": "full",
        "notes": "Сопоставление role/title из LDAP для администратора платформы.",
        "is_active": 1,
        "sort_order": 110,
    },
    {
        "source_system": "ldap",
        "source_role_key": "",
        "source_role_label": "Заведующий отделением / руководитель подразделения",
        "hospital_role_key": "department_head",
        "hospital_role_label": "Заведующий отделением / руководитель подразделения",
        "access_scope": "department",
        "notes": "Сопоставление role/title из LDAP для руководителя подразделения.",
        "is_active": 1,
        "sort_order": 120,
    },
    {
        "source_system": "ldap",
        "source_role_key": "",
        "source_role_label": "Врач / сотрудник подразделения",
        "hospital_role_key": "clinician",
        "hospital_role_label": "Врач / сотрудник подразделения",
        "access_scope": "own",
        "notes": "Сопоставление role/title из LDAP для врача и сотрудника подразделения.",
        "is_active": 1,
        "sort_order": 130,
    },
    {
        "source_system": "ldap",
        "source_role_key": "",
        "source_role_label": "Старшая медсестра / координатор отделения",
        "hospital_role_key": "nurse_coordinator",
        "hospital_role_label": "Старшая медсестра / координатор отделения",
        "access_scope": "department",
        "notes": "Сопоставление role/title из LDAP для старшей медсестры и координатора.",
        "is_active": 1,
        "sort_order": 135,
    },
    {
        "source_system": "ldap",
        "source_role_key": "",
        "source_role_label": "Регистратура / заявитель",
        "hospital_role_key": "registry_operator",
        "hospital_role_label": "Регистратура / заявитель",
        "access_scope": "registry",
        "notes": "Сопоставление role/title из LDAP для регистратуры.",
        "is_active": 1,
        "sort_order": 140,
    },
    {
        "source_system": "ldap",
        "source_role_key": "",
        "source_role_label": "Канцелярия / делопроизводство",
        "hospital_role_key": "records_office",
        "hospital_role_label": "Канцелярия / делопроизводство",
        "access_scope": "office",
        "notes": "Сопоставление role/title из LDAP для канцелярии.",
        "is_active": 1,
        "sort_order": 150,
    },
]

DEFAULT_DOCUMENT_ROUTE_DEFINITIONS = [
    {
        "route_key": "incoming_registration",
        "route_label": "Входящая регистрация",
        "route_group": "hospital",
        "default_doc_status_name": "На регистрации",
        "final_doc_status_name": "Архивирован",
        "status_sequence": ["Черновик", "На регистрации", "Зарегистрирован", "На ознакомлении", "Архивирован"],
        "participant_role_keys": ["registry_operator", "records_office"],
        "requires_registration": 1,
        "requires_approval": 0,
        "notes": "Канцелярский маршрут для входящих документов и первичного учета.",
        "is_active": 1,
        "sort_order": 10,
    },
    {
        "route_key": "outgoing_approval",
        "route_label": "Исходящее письмо / согласование",
        "route_group": "hospital",
        "default_doc_status_name": "На согласовании",
        "final_doc_status_name": "Архивирован",
        "status_sequence": ["Черновик", "На согласовании", "На утверждении", "Подписан", "На регистрации", "Зарегистрирован", "Архивирован"],
        "participant_role_keys": ["clinician", "department_head", "records_office"],
        "requires_registration": 1,
        "requires_approval": 1,
        "notes": "Исходящий документ с согласованием подразделения и регистрацией через канцелярский контур.",
        "is_active": 1,
        "sort_order": 20,
    },
    {
        "route_key": "internal_order",
        "route_label": "Внутренний приказ / распоряжение",
        "route_group": "hospital",
        "default_doc_status_name": "На согласовании",
        "final_doc_status_name": "Архивирован",
        "status_sequence": ["Черновик", "На согласовании", "На утверждении", "Подписан", "На ознакомлении", "Архивирован"],
        "participant_role_keys": ["department_head", "records_office"],
        "requires_registration": 0,
        "requires_approval": 1,
        "notes": "Внутренний маршрут приказа или распоряжения по подразделению.",
        "is_active": 1,
        "sort_order": 30,
    },
    {
        "route_key": "clinical_document",
        "route_label": "Медицинская документация отделения",
        "route_group": "hospital",
        "default_doc_status_name": "На согласовании",
        "final_doc_status_name": "Архивирован",
        "status_sequence": ["Черновик", "На согласовании", "На утверждении", "Подписан", "На регистрации", "Зарегистрирован", "Архивирован"],
        "participant_role_keys": ["clinician", "nurse_coordinator", "department_head", "records_office"],
        "requires_registration": 1,
        "requires_approval": 1,
        "notes": "Маршрут для документов отделения и внутренней медицинской документации.",
        "is_active": 1,
        "sort_order": 40,
    },
    {
        "route_key": "patient_route",
        "route_label": "Пациент / направление / выписка",
        "route_group": "hospital",
        "default_doc_status_name": "На согласовании",
        "final_doc_status_name": "Архивирован",
        "status_sequence": ["Черновик", "На согласовании", "На утверждении", "Подписан", "На регистрации", "Зарегистрирован", "Архивирован"],
        "participant_role_keys": ["clinician", "nurse_coordinator", "department_head", "registry_operator", "records_office"],
        "requires_registration": 1,
        "requires_approval": 1,
        "notes": "Маршрут пациента, направления и выписки с участием регистратора и отделения.",
        "is_active": 1,
        "sort_order": 50,
    },
    {
        "route_key": "contract_procurement",
        "route_label": "Договор / закупка / МТЗ",
        "route_group": "hospital",
        "default_doc_status_name": "На согласовании",
        "final_doc_status_name": "Архивирован",
        "status_sequence": ["Черновик", "На согласовании", "На утверждении", "Подписан", "На регистрации", "Зарегистрирован", "Архивирован"],
        "participant_role_keys": ["nurse_coordinator", "department_head", "records_office"],
        "requires_registration": 1,
        "requires_approval": 1,
        "notes": "Договорной и закупочный маршрут, включая заявки МТЗ.",
        "is_active": 1,
        "sort_order": 60,
    },
    {
        "route_key": "staff_acknowledgement",
        "route_label": "Ознакомление персонала",
        "route_group": "hospital",
        "default_doc_status_name": "На ознакомлении",
        "final_doc_status_name": "Архивирован",
        "status_sequence": ["Черновик", "На согласовании", "На утверждении", "Подписан", "На ознакомлении", "Архивирован"],
        "participant_role_keys": ["department_head", "nurse_coordinator", "clinician"],
        "requires_registration": 0,
        "requires_approval": 1,
        "notes": "Ознакомление персонала с внутренними документами и приказами.",
        "is_active": 1,
        "sort_order": 70,
    },
    {
        "route_key": "archive_closure",
        "route_label": "Архив / закрытие",
        "route_group": "hospital",
        "default_doc_status_name": "Архивирован",
        "final_doc_status_name": "Архивирован",
        "status_sequence": ["Зарегистрирован", "Архивирован"],
        "participant_role_keys": ["records_office", "hospital_admin"],
        "requires_registration": 1,
        "requires_approval": 0,
        "notes": "Финальный архивный маршрут для закрытых документов и завершенных кейсов.",
        "is_active": 1,
        "sort_order": 80,
    },
]

STATUS_MAPPING_DB_FIELDS = (
    "match_type",
    "match_value",
    "request_status_name",
    "doc_status_name",
    "integration_status_name",
    "notes",
    "is_active",
    "sort_order",
    "created_at",
    "updated_at",
)

FIELD_MAPPING_DB_FIELDS = (
    "source_system",
    "source_entity",
    "source_field_key",
    "target_system",
    "target_entity",
    "target_field_key",
    "direction",
    "notes",
    "is_required",
    "is_active",
    "sort_order",
    "created_at",
    "updated_at",
)

IDENTITY_SOURCE_DB_FIELDS = (
    "source_key",
    "source_label",
    "provider_type",
    "source_system",
    "sync_mode",
    "host",
    "port",
    "ssl_mode",
    "base_dn",
    "user_base_dn",
    "group_base_dn",
    "login_attribute",
    "display_name_attribute",
    "email_attribute",
    "department_attribute",
    "role_attribute",
    "bind_dn",
    "bind_password_env_key",
    "notes",
    "metadata_json",
    "is_active",
    "is_default",
    "created_at",
    "updated_at",
)

HOSPITAL_ROLE_MAPPING_DB_FIELDS = (
    "source_system",
    "source_role_key",
    "source_role_label",
    "hospital_role_key",
    "hospital_role_label",
    "access_scope",
    "notes",
    "is_active",
    "sort_order",
    "created_at",
    "updated_at",
)

DOCUMENT_ROUTE_DEFINITION_DB_FIELDS = (
    "route_key",
    "route_label",
    "route_group",
    "default_doc_status_name",
    "final_doc_status_name",
    "status_sequence_json",
    "participant_role_keys_json",
    "requires_registration",
    "requires_approval",
    "notes",
    "is_active",
    "sort_order",
    "created_at",
    "updated_at",
)

USER_PROFILE_MUTABLE_FIELDS = (
    "source_display_name",
    "source_email",
    "source_department",
    "source_role_key",
    "source_role_label",
    "source_profile_url",
    "source_folder_url",
    "linked_system",
    "linked_user_id",
    "linked_username",
    "linked_display_name",
    "linked_email",
    "linked_department",
    "linked_role_key",
    "linked_role_label",
    "sync_status",
    "notes",
    "metadata_json",
    "updated_at",
)


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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_failures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL DEFAULT 'bridge',
                job_name TEXT NOT NULL,
                external_system TEXT NOT NULL DEFAULT '',
                external_entity TEXT NOT NULL DEFAULT '',
                external_item_id TEXT NOT NULL DEFAULT '',
                link_id INTEGER,
                message TEXT NOT NULL,
                context_json TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'open',
                retry_count INTEGER NOT NULL DEFAULT 0,
                last_retry_at TEXT NOT NULL DEFAULT '',
                last_result_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_sync_failures_status
            ON sync_failures (status, updated_at DESC)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_sync_failures_external
            ON sync_failures (source, job_name, external_system, external_entity, external_item_id)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_status_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_type TEXT NOT NULL DEFAULT 'contains',
                match_value TEXT NOT NULL,
                request_status_name TEXT NOT NULL DEFAULT '',
                doc_status_name TEXT NOT NULL DEFAULT '',
                integration_status_name TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 1,
                sort_order INTEGER NOT NULL DEFAULT 100,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_sync_status_mappings_active
            ON sync_status_mappings (is_active, sort_order, id)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_field_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_system TEXT NOT NULL DEFAULT 'rukovoditel',
                source_entity TEXT NOT NULL,
                source_field_key TEXT NOT NULL,
                target_system TEXT NOT NULL DEFAULT 'bridge',
                target_entity TEXT NOT NULL DEFAULT 'metadata',
                target_field_key TEXT NOT NULL,
                direction TEXT NOT NULL DEFAULT 'push',
                notes TEXT NOT NULL DEFAULT '',
                is_required INTEGER NOT NULL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1,
                sort_order INTEGER NOT NULL DEFAULT 100,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_sync_field_mappings_active
            ON sync_field_mappings (source_entity, direction, is_active, sort_order, id)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_directory_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_system TEXT NOT NULL DEFAULT 'naudoc',
                source_username TEXT NOT NULL,
                source_display_name TEXT NOT NULL DEFAULT '',
                source_email TEXT NOT NULL DEFAULT '',
                source_department TEXT NOT NULL DEFAULT '',
                source_role_key TEXT NOT NULL DEFAULT '',
                source_role_label TEXT NOT NULL DEFAULT '',
                source_profile_url TEXT NOT NULL DEFAULT '',
                source_folder_url TEXT NOT NULL DEFAULT '',
                linked_system TEXT NOT NULL DEFAULT '',
                linked_user_id TEXT NOT NULL DEFAULT '',
                linked_username TEXT NOT NULL DEFAULT '',
                linked_display_name TEXT NOT NULL DEFAULT '',
                linked_email TEXT NOT NULL DEFAULT '',
                linked_department TEXT NOT NULL DEFAULT '',
                linked_role_key TEXT NOT NULL DEFAULT '',
                linked_role_label TEXT NOT NULL DEFAULT '',
                sync_status TEXT NOT NULL DEFAULT 'unmatched',
                notes TEXT NOT NULL DEFAULT '',
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_user_directory_profiles_source
            ON user_directory_profiles (source_system, source_username)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_user_directory_profiles_status
            ON user_directory_profiles (sync_status, source_system, source_username)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS identity_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_key TEXT NOT NULL,
                source_label TEXT NOT NULL,
                provider_type TEXT NOT NULL DEFAULT 'manual',
                source_system TEXT NOT NULL DEFAULT '',
                sync_mode TEXT NOT NULL DEFAULT 'manual',
                host TEXT NOT NULL DEFAULT '',
                port INTEGER NOT NULL DEFAULT 0,
                ssl_mode TEXT NOT NULL DEFAULT 'none',
                base_dn TEXT NOT NULL DEFAULT '',
                user_base_dn TEXT NOT NULL DEFAULT '',
                group_base_dn TEXT NOT NULL DEFAULT '',
                login_attribute TEXT NOT NULL DEFAULT 'uid',
                display_name_attribute TEXT NOT NULL DEFAULT 'cn',
                email_attribute TEXT NOT NULL DEFAULT 'mail',
                department_attribute TEXT NOT NULL DEFAULT 'department',
                role_attribute TEXT NOT NULL DEFAULT 'title',
                bind_dn TEXT NOT NULL DEFAULT '',
                bind_password_env_key TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                metadata_json TEXT NOT NULL DEFAULT '{}',
                is_active INTEGER NOT NULL DEFAULT 1,
                is_default INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_identity_sources_key
            ON identity_sources (source_key)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_identity_sources_active
            ON identity_sources (is_active, provider_type, source_system, source_key)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS hospital_role_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_system TEXT NOT NULL DEFAULT 'rukovoditel',
                source_role_key TEXT NOT NULL DEFAULT '',
                source_role_label TEXT NOT NULL DEFAULT '',
                hospital_role_key TEXT NOT NULL,
                hospital_role_label TEXT NOT NULL,
                access_scope TEXT NOT NULL DEFAULT 'custom',
                notes TEXT NOT NULL DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 1,
                sort_order INTEGER NOT NULL DEFAULT 100,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_hospital_role_mappings_unique
            ON hospital_role_mappings (source_system, source_role_key, source_role_label, hospital_role_key)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_hospital_role_mappings_active
            ON hospital_role_mappings (is_active, source_system, sort_order, id)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS document_route_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_key TEXT NOT NULL,
                route_label TEXT NOT NULL,
                route_group TEXT NOT NULL DEFAULT 'hospital',
                default_doc_status_name TEXT NOT NULL DEFAULT '',
                final_doc_status_name TEXT NOT NULL DEFAULT '',
                status_sequence_json TEXT NOT NULL DEFAULT '[]',
                participant_role_keys_json TEXT NOT NULL DEFAULT '[]',
                requires_registration INTEGER NOT NULL DEFAULT 0,
                requires_approval INTEGER NOT NULL DEFAULT 0,
                notes TEXT NOT NULL DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 1,
                sort_order INTEGER NOT NULL DEFAULT 100,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_document_route_definitions_key
            ON document_route_definitions (route_key)
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_document_route_definitions_label
            ON document_route_definitions (route_label)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_document_route_definitions_active
            ON document_route_definitions (is_active, route_group, sort_order, id)
            """
        )
        ensure_column(conn, "user_directory_profiles", "source_email", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "user_directory_profiles", "source_department", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "user_directory_profiles", "source_role_key", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "user_directory_profiles", "source_role_label", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "user_directory_profiles", "linked_email", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "user_directory_profiles", "linked_department", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "user_directory_profiles", "linked_role_key", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "user_directory_profiles", "linked_role_label", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "identity_sources", "last_check_at", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "identity_sources", "last_check_status", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "identity_sources", "last_check_message", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "identity_sources", "last_sync_at", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "identity_sources", "last_sync_status", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "identity_sources", "last_sync_message", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "identity_sources", "last_synced_count", "INTEGER NOT NULL DEFAULT 0")
        seed_default_status_mappings(conn)
        seed_default_field_mappings(conn)
        seed_default_identity_sources(conn)
        seed_default_hospital_role_mappings(conn)
        seed_default_document_route_definitions(conn)
        for row in conn.execute("SELECT id, naudoc_url FROM document_links").fetchall():
            link_id, naudoc_url = row[0], row[1]
            normalized_url = normalize_naudoc_url(naudoc_url)
            if normalized_url != naudoc_url:
                conn.execute(
                    "UPDATE document_links SET naudoc_url = ?, updated_at = ? WHERE id = ?",
                    (normalized_url, utcnow_iso(), link_id),
                )
        conn.commit()


def db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row):
    item = dict(row)
    item["naudoc_url"] = normalize_naudoc_url(item.get("naudoc_url"))
    item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
    return item


def failure_row_to_dict(row):
    item = dict(row)
    item["context"] = json.loads(item.pop("context_json") or "{}")
    item["last_result"] = json.loads(item.pop("last_result_json") or "{}")
    return item


def user_profile_row_to_dict(row):
    item = dict(row)
    item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
    return item


def identity_source_row_to_dict(row):
    item = dict(row)
    item["is_active"] = bool(item.get("is_active"))
    item["is_default"] = bool(item.get("is_default"))
    item["last_synced_count"] = normalize_int(item.get("last_synced_count")) or 0
    item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
    return item


def hospital_role_mapping_row_to_dict(row):
    item = dict(row)
    item["is_active"] = bool(item.get("is_active"))
    return item


def document_route_definition_row_to_dict(row):
    item = dict(row)
    item["is_active"] = bool(item.get("is_active"))
    item["requires_registration"] = bool(item.get("requires_registration"))
    item["requires_approval"] = bool(item.get("requires_approval"))
    item["status_sequence"] = json.loads(item.pop("status_sequence_json") or "[]")
    item["participant_role_keys"] = json.loads(item.pop("participant_role_keys_json") or "[]")
    return item


def status_mapping_row_to_dict(row):
    item = dict(row)
    item["is_active"] = bool(item.get("is_active"))
    return item


def field_mapping_row_to_dict(row):
    item = dict(row)
    item["is_active"] = bool(item.get("is_active"))
    item["is_required"] = bool(item.get("is_required"))
    return item


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def normalize_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def normalize_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return normalize_text(value).lower() in {"1", "true", "yes", "on"}


def normalize_lower(value):
    return normalize_text(value).casefold()


def normalize_text_list(value):
    if isinstance(value, list):
        raw_items = value
    else:
        raw_items = re.split(r"[\n,;]+", normalize_text(value))
    result = []
    seen = set()
    for item in raw_items:
        normalized = normalize_text(item)
        if not normalized:
            continue
        key = normalized.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(normalized)
    return result


def ensure_column(conn, table_name, column_name, column_definition):
    existing_columns = {
        row[1]
        for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    if column_name not in existing_columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


def fetch_table_row_by_id(conn, table_name, row_id):
    return conn.execute(f"SELECT * FROM {table_name} WHERE id = ?", (row_id,)).fetchone()


def insert_table_row(conn, table_name, field_names, data):
    placeholders = ", ".join(["?"] * len(field_names))
    columns = ", ".join(field_names)
    values = tuple(data[field_name] for field_name in field_names)
    cursor = conn.execute(
        f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
        values,
    )
    return fetch_table_row_by_id(conn, table_name, cursor.lastrowid)


def update_table_row(conn, table_name, row_id, existing, field_names, data):
    if existing is None:
        return None

    update_fields = [field_name for field_name in field_names if field_name != "created_at"]
    assignments = ", ".join(f"{field_name} = ?" for field_name in update_fields)
    values = tuple(data[field_name] for field_name in update_fields) + (row_id,)
    conn.execute(
        f"UPDATE {table_name} SET {assignments} WHERE id = ?",
        values,
    )
    return fetch_table_row_by_id(conn, table_name, row_id)


def create_configured_row(conn, table_name, field_names, payload_builder, payload, *, unique_default_field=None):
    data = payload_builder(payload)
    row = insert_table_row(conn, table_name, field_names, data)
    if unique_default_field and data.get(unique_default_field):
        conn.execute(
            f"UPDATE {table_name} SET {unique_default_field} = 0 WHERE id != ?",
            (row["id"],),
        )
        row = fetch_table_row_by_id(conn, table_name, row["id"])
    return row


def update_configured_row(
    conn,
    table_name,
    row_id,
    field_names,
    payload_builder,
    payload,
    *,
    unique_default_field=None,
):
    existing = fetch_table_row_by_id(conn, table_name, row_id)
    data = payload_builder(payload)
    row = update_table_row(conn, table_name, row_id, existing, field_names, data)
    if row is None:
        return None
    if unique_default_field and data.get(unique_default_field):
        conn.execute(
            f"UPDATE {table_name} SET {unique_default_field} = 0 WHERE id != ?",
            (row_id,),
        )
        row = fetch_table_row_by_id(conn, table_name, row_id)
    return row


def persist_user_profile_fields(conn, profile_id, data):
    assignments = ", ".join(f"{field_name} = ?" for field_name in USER_PROFILE_MUTABLE_FIELDS)
    values = tuple(data[field_name] for field_name in USER_PROFILE_MUTABLE_FIELDS) + (profile_id,)
    conn.execute(
        f"UPDATE user_directory_profiles SET {assignments} WHERE id = ?",
        values,
    )
    return conn.execute("SELECT * FROM user_directory_profiles WHERE id = ?", (profile_id,)).fetchone()


def apply_form_checkbox_fields(payload, field_names):
    if not request.form:
        return payload
    for field_name in field_names:
        payload[field_name] = "1" if request.form.get(field_name) else "0"
    return payload


def seed_default_status_mappings(conn):
    existing_count = conn.execute("SELECT COUNT(*) AS cnt FROM sync_status_mappings").fetchone()[0]
    if existing_count:
        return

    now = utcnow_iso()
    for row in DEFAULT_STATUS_MAPPINGS:
        conn.execute(
            """
            INSERT INTO sync_status_mappings (
                match_type,
                match_value,
                request_status_name,
                doc_status_name,
                integration_status_name,
                notes,
                is_active,
                sort_order,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                normalize_text(row.get("match_type")) or "contains",
                normalize_text(row.get("match_value")),
                normalize_text(row.get("request_status_name")),
                normalize_text(row.get("doc_status_name")),
                normalize_text(row.get("integration_status_name")),
                normalize_text(row.get("notes")),
                1,
                normalize_int(row.get("sort_order")) or 100,
                now,
                now,
            ),
        )


def seed_default_field_mappings(conn):
    now = utcnow_iso()
    for row in DEFAULT_FIELD_MAPPINGS:
        source_system = normalize_text(row.get("source_system")) or "rukovoditel"
        source_entity = normalize_text(row.get("source_entity"))
        source_field_key = normalize_text(row.get("source_field_key"))
        target_system = normalize_text(row.get("target_system")) or "bridge"
        target_entity = normalize_text(row.get("target_entity")) or "metadata"
        target_field_key = normalize_text(row.get("target_field_key"))
        direction = normalize_text(row.get("direction")) or "push"

        existing = conn.execute(
            """
            SELECT id
            FROM sync_field_mappings
            WHERE source_system = ?
              AND source_entity = ?
              AND source_field_key = ?
              AND target_system = ?
              AND target_entity = ?
              AND target_field_key = ?
              AND direction = ?
            LIMIT 1
            """,
            (
                source_system,
                source_entity,
                source_field_key,
                target_system,
                target_entity,
                target_field_key,
                direction,
            ),
        ).fetchone()
        if existing is not None:
            continue

        conn.execute(
            """
            INSERT INTO sync_field_mappings (
                source_system,
                source_entity,
                source_field_key,
                target_system,
                target_entity,
                target_field_key,
                direction,
                notes,
                is_required,
                is_active,
                sort_order,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_system,
                source_entity,
                source_field_key,
                target_system,
                target_entity,
                target_field_key,
                direction,
                normalize_text(row.get("notes")),
                1 if normalize_bool(row.get("is_required"), False) else 0,
                1 if normalize_bool(row.get("is_active"), True) else 0,
                normalize_int(row.get("sort_order")) or 100,
                now,
                now,
            ),
        )


def seed_default_identity_sources(conn):
    existing_keys = {
        row[0]
        for row in conn.execute("SELECT source_key FROM identity_sources").fetchall()
    }
    now = utcnow_iso()
    for row in DEFAULT_IDENTITY_SOURCES:
        if row["source_key"] in existing_keys:
            continue

        conn.execute(
            """
            INSERT INTO identity_sources (
                source_key,
                source_label,
                provider_type,
                source_system,
                sync_mode,
                host,
                port,
                ssl_mode,
                base_dn,
                user_base_dn,
                group_base_dn,
                login_attribute,
                display_name_attribute,
                email_attribute,
                department_attribute,
                role_attribute,
                bind_dn,
                bind_password_env_key,
                notes,
                metadata_json,
                is_active,
                is_default,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["source_key"],
                row["source_label"],
                row["provider_type"],
                row["source_system"],
                row["sync_mode"],
                row["host"],
                row["port"],
                row["ssl_mode"],
                row["base_dn"],
                row["user_base_dn"],
                row["group_base_dn"],
                row["login_attribute"],
                row["display_name_attribute"],
                row["email_attribute"],
                row["department_attribute"],
                row["role_attribute"],
                row["bind_dn"],
                row["bind_password_env_key"],
                row["notes"],
                "{}",
                row["is_active"],
                row["is_default"],
                now,
                now,
            ),
        )


def seed_default_hospital_role_mappings(conn):
    existing_keys = {
        (
            row[0],
            row[1],
            row[2],
            row[3],
        )
        for row in conn.execute(
            """
            SELECT source_system, source_role_key, source_role_label, hospital_role_key
            FROM hospital_role_mappings
            """
        ).fetchall()
    }
    now = utcnow_iso()
    for row in DEFAULT_HOSPITAL_ROLE_MAPPINGS:
        key = (
            row["source_system"],
            row["source_role_key"],
            row["source_role_label"],
            row["hospital_role_key"],
        )
        if key in existing_keys:
            continue

        conn.execute(
            """
            INSERT INTO hospital_role_mappings (
                source_system,
                source_role_key,
                source_role_label,
                hospital_role_key,
                hospital_role_label,
                access_scope,
                notes,
                is_active,
                sort_order,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["source_system"],
                row["source_role_key"],
                row["source_role_label"],
                row["hospital_role_key"],
                row["hospital_role_label"],
                row["access_scope"],
                row["notes"],
                row["is_active"],
                row["sort_order"],
                now,
                now,
            ),
        )


def seed_default_document_route_definitions(conn):
    existing_keys = {
        row[0]
        for row in conn.execute("SELECT route_key FROM document_route_definitions").fetchall()
    }
    now = utcnow_iso()
    for row in DEFAULT_DOCUMENT_ROUTE_DEFINITIONS:
        if row["route_key"] in existing_keys:
            continue

        conn.execute(
            """
            INSERT INTO document_route_definitions (
                route_key,
                route_label,
                route_group,
                default_doc_status_name,
                final_doc_status_name,
                status_sequence_json,
                participant_role_keys_json,
                requires_registration,
                requires_approval,
                notes,
                is_active,
                sort_order,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["route_key"],
                row["route_label"],
                row.get("route_group", "hospital"),
                row.get("default_doc_status_name", ""),
                row.get("final_doc_status_name", ""),
                json.dumps(row.get("status_sequence", []), ensure_ascii=False),
                json.dumps(row.get("participant_role_keys", []), ensure_ascii=False),
                1 if normalize_bool(row.get("requires_registration"), False) else 0,
                1 if normalize_bool(row.get("requires_approval"), False) else 0,
                row.get("notes", ""),
                1 if normalize_bool(row.get("is_active"), True) else 0,
                normalize_int(row.get("sort_order")) or 100,
                now,
                now,
            ),
        )


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


def naudoc_internal_url(relative_path=""):
    base = NAUDOC_BASE_URL.rstrip("/")
    relative_path = normalize_text(relative_path).lstrip("/")
    return f"{base}/{relative_path}" if relative_path else base


def naudoc_public_url(relative_path=""):
    base = NAUDOC_PUBLIC_URL.rstrip("/")
    relative_path = normalize_text(relative_path).lstrip("/")
    return normalize_naudoc_url(f"{base}/{relative_path}" if relative_path else base)


def extract_naudoc_relative_path(url):
    normalized = normalize_naudoc_url(url)
    if not normalized:
        return ""

    known_bases = [
        NAUDOC_PUBLIC_URL.rstrip("/"),
        NAUDOC_BASE_URL.rstrip("/"),
        "http://localhost:18080/docs",
        "http://host.docker.internal:18080/docs",
        "https://localhost:18443/docs",
    ]

    for base in dict.fromkeys(filter(None, known_bases)):
        if not normalized.startswith(base):
            continue
        relative = normalized[len(base):].strip("/")
        if not relative:
            return ""
        return relative

    return ""


def is_specific_naudoc_object_url(url):
    relative_path = extract_naudoc_relative_path(url)
    if not relative_path:
        return False
    return relative_path not in {"storage", "home"}


def naudoc_form_encode(payload):
    items = []
    for key, value in payload.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            for entry in value:
                if entry is None:
                    continue
                items.append((key, str(entry)))
            continue
        items.append((key, str(value)))

    return urllib.parse.urlencode(
        items,
        doseq=True,
        encoding="cp1251",
        errors="xmlcharrefreplace",
    ).encode("ascii")


def naudoc_request(method, url, *, form_data=None, allow_redirects=True):
    headers = {}
    data = None
    if form_data is not None:
        data = naudoc_form_encode(form_data)
        headers["Content-Type"] = "application/x-www-form-urlencoded; charset=windows-1251"

    return requests.request(
        method,
        url,
        data=data,
        headers=headers,
        auth=(NAUDOC_USERNAME, NAUDOC_PASSWORD),
        timeout=REQUEST_TIMEOUT,
        verify=False,
        allow_redirects=allow_redirects,
    )


def naudoc_decode_response_text(response):
    charset = "cp1251"
    content_type = normalize_text(response.headers.get("Content-Type"))
    match = re.search(r"charset=([A-Za-z0-9_-]+)", content_type, re.IGNORECASE)
    if match:
        charset = match.group(1)
    return response.content.decode(charset, "ignore")


def naudoc_get_text(url):
    response = naudoc_request("GET", url)
    response.raise_for_status()
    return naudoc_decode_response_text(response)


def naudoc_object_exists(relative_path):
    relative_path = normalize_text(relative_path).strip("/")
    if not relative_path:
        return False
    response = naudoc_request("GET", naudoc_internal_url(relative_path))
    return response.ok


def safe_naudoc_fragment(value):
    value = normalize_lower(value)
    if not value:
        return "item"
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "item"


def build_naudoc_document_id(link):
    entity = safe_naudoc_fragment(link["external_entity"])
    item_id = safe_naudoc_fragment(link["external_item_id"])
    return f"bridge_{entity}_{item_id}"


def build_naudoc_document_title(link):
    metadata = link.get("metadata") or {}
    projection = metadata.get("naudoc_projection") or {}
    document_projection = projection.get("document") or {}
    return (
        normalize_text(document_projection.get("title"))
        or normalize_text(link.get("naudoc_title"))
        or normalize_text(link.get("external_title"))
        or f"Bridge {link['external_entity']} #{link['external_item_id']}"
    )


def build_naudoc_document_description(link):
    title = build_naudoc_document_title(link)
    return (
        f"Автоматическая публикация Bridge для {link['external_entity']} #{link['external_item_id']}."
        f" Источник: {title}"
    )


def extract_link_document_route_context(link):
    metadata = link.get("metadata") or {}
    projection = metadata.get("naudoc_projection") or {}
    workflow_projection = projection.get("workflow") or {}

    route_label = normalize_text(
        workflow_projection.get("route_label")
        or metadata.get("document_route")
    )
    route_key = normalize_text(workflow_projection.get("route_key"))

    if not route_label and not route_key:
        return None

    with closing(db_connection()) as conn:
        definition = resolve_document_route_definition(
            fetch_active_document_route_definitions(conn),
            route_label,
            route_key,
        )

    return {
        "route_label": route_label or (definition.get("route_label") if definition else ""),
        "route_key": route_key or (definition.get("route_key") if definition else ""),
        "definition": definition,
    }


def build_naudoc_document_body(link):
    metadata = link.get("metadata") or {}
    projection = metadata.get("naudoc_projection") or {}
    document_projection = projection.get("document") or {}
    route_context = extract_link_document_route_context(link)

    source_links = []
    for key in (
        "source_request_url",
        "source_project_url",
        "source_doc_card_url",
        "request_url",
        "project_url",
        "doc_card_url",
    ):
        value = normalize_text(document_projection.get(key) or metadata.get(key))
        if value and value not in source_links:
            source_links.append(value)

    details = [
        ("Источник", f"{link['external_system']} / {link['external_entity']} / {link['external_item_id']}"),
        ("Статус синхронизации", normalize_text(link.get("sync_status")) or "pending_nau_doc"),
        ("Название записи", normalize_text(link.get("external_title"))),
        ("Название документа", build_naudoc_document_title(link)),
    ]

    table_rows = "\n".join(
        f"<tr><th align=\"left\">{html_escape(label)}</th><td>{html_escape(value)}</td></tr>"
        for label, value in details
        if value
    )

    links_html = ""
    if source_links:
        links_html = "<ul>" + "".join(
            f"<li><a href=\"{html_escape(url)}\">{html_escape(url)}</a></li>"
            for url in source_links
        ) + "</ul>"

    route_html = "<p>Маршрут документа пока не задан в рабочей карточке.</p>"
    if route_context:
        definition = route_context.get("definition") or {}
        participants = definition.get("participant_role_keys") or []
        status_sequence = definition.get("status_sequence") or []
        route_rows = [
            ("Маршрут", route_context.get("route_label")),
            ("Ключ маршрута", route_context.get("route_key")),
            ("Стартовый статус", definition.get("default_doc_status_name")),
            ("Финальный статус", definition.get("final_doc_status_name")),
            ("Регистрация обязательна", "Да" if definition.get("requires_registration") else "Нет"),
            ("Утверждение обязательно", "Да" if definition.get("requires_approval") else "Нет"),
        ]
        route_table_rows = "\n".join(
            f"<tr><th align=\"left\">{html_escape(label)}</th><td>{html_escape(value)}</td></tr>"
            for label, value in route_rows
            if value
        )
        participants_html = "<p>Участники маршрута не заданы.</p>"
        if participants:
            participants_html = "<ul>" + "".join(
                f"<li>{html_escape(role_key)}</li>" for role_key in participants
            ) + "</ul>"
        statuses_html = "<p>Последовательность статусов пока не задана.</p>"
        if status_sequence:
            statuses_html = "<ol>" + "".join(
                f"<li>{html_escape(status_name)}</li>" for status_name in status_sequence
            ) + "</ol>"
        route_html = (
            f"<table>{route_table_rows}</table>"
            "<h4>Участники маршрута</h4>"
            f"{participants_html}"
            "<h4>Последовательность статусов</h4>"
            f"{statuses_html}"
        )

    projection_json = html_escape(
        json.dumps(projection, ensure_ascii=False, indent=2, sort_keys=True)
        if projection
        else "{}"
    )

    return (
        "<h2>Связка с рабочим контуром</h2>"
        "<p>Документ автоматически создан или обновлен из единой платформы документооборота.</p>"
        f"<table>{table_rows}</table>"
        "<h3>Маршрут документа</h3>"
        f"{route_html}"
        "<h3>Исходные ссылки</h3>"
        f"{links_html or '<p>Прямые ссылки источника пока не переданы.</p>'}"
        "<h3>Проекция полей</h3>"
        f"<pre>{projection_json}</pre>"
    )


def fetch_naudoc_safety_belt(relative_path):
    html = naudoc_get_text(naudoc_internal_url(f"{relative_path}/document_edit_form"))
    match = re.search(r'name="SafetyBelt" value="([^"]*)"', html)
    if not match:
        raise RuntimeError(f"Failed to read NauDoc SafetyBelt for '{relative_path}'")
    return match.group(1)


def ensure_naudoc_document_path(link):
    existing_relative_path = extract_naudoc_relative_path(link.get("naudoc_url"))
    if is_specific_naudoc_object_url(link.get("naudoc_url")) and naudoc_object_exists(existing_relative_path):
        return existing_relative_path, False

    doc_id = build_naudoc_document_id(link)
    relative_path = f"storage/{doc_id}"
    if naudoc_object_exists(relative_path):
        return relative_path, False

    response = naudoc_request(
        "POST",
        naudoc_internal_url("storage/invoke_factory"),
        form_data={
            "type_name": "HTMLDocument",
            "id": doc_id,
            "title": build_naudoc_document_title(link),
            "cat_id": "Document",
        },
    )
    response.raise_for_status()

    if not naudoc_object_exists(relative_path):
        raise RuntimeError(f"NauDoc did not create expected object '{relative_path}'")

    return relative_path, True


def update_naudoc_document(relative_path, *, title, description, body):
    metadata_response = naudoc_request(
        "POST",
        naudoc_internal_url(f"{relative_path}/metadata_edit"),
        form_data={
            "title": title,
            "description": description,
        },
    )
    metadata_response.raise_for_status()

    safety_belt = fetch_naudoc_safety_belt(relative_path)
    body_response = naudoc_request(
        "POST",
        naudoc_internal_url(f"{relative_path}/document_edit"),
        form_data={
            "text:text": body,
            "text_format": "html",
            "SafetyBelt": safety_belt,
        },
    )
    body_response.raise_for_status()


def promote_writeback_sync_status(sync_status):
    current = normalize_text(sync_status)
    if not current or current == "pending_nau_doc":
        return "linked"
    return current


def writeback_link_to_naudoc(conn, link_id):
    existing = get_link_by_id(conn, link_id)
    if existing is None:
        raise RuntimeError("Link not found")

    link = row_to_dict(existing)
    relative_path, created = ensure_naudoc_document_path(link)
    title = build_naudoc_document_title(link)
    description = build_naudoc_document_description(link)
    body = build_naudoc_document_body(link)

    update_naudoc_document(
        relative_path,
        title=title,
        description=description,
        body=body,
    )

    metadata = dict(link.get("metadata") or {})
    metadata["naudoc_writeback"] = {
        "status": "created" if created else "updated",
        "relative_path": relative_path,
        "updated_at": utcnow_iso(),
    }

    public_url = naudoc_public_url(relative_path)
    conn.execute(
        """
        UPDATE document_links
        SET naudoc_url = ?,
            naudoc_title = ?,
            sync_status = ?,
            metadata_json = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            public_url,
            title,
            promote_writeback_sync_status(existing["sync_status"]),
            json.dumps(metadata, ensure_ascii=False, sort_keys=True),
            utcnow_iso(),
            link_id,
        ),
    )
    row = get_link_by_id(conn, link_id)
    return row_to_dict(row), {
        "status": metadata["naudoc_writeback"]["status"],
        "relative_path": relative_path,
        "public_url": public_url,
        "title": title,
    }


def fetch_nau_doc_status():
    health_url = naudoc_internal_url("manage_users_form")
    try:
        response = requests.get(
            health_url,
            auth=(NAUDOC_USERNAME, NAUDOC_PASSWORD),
            timeout=REQUEST_TIMEOUT,
        )
        return {
            "ok": response.ok,
            "status_code": response.status_code,
            "url": health_url,
            "title_hint": "NauDoc" if "manage_users_form" in response.url or "docs" in response.url else "",
        }
    except requests.RequestException as exc:
        return {
            "ok": False,
            "status_code": None,
            "url": health_url,
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


def merge_metadata_json(existing_metadata_json, metadata):
    if metadata is None:
        return existing_metadata_json

    merged_metadata = json.loads(existing_metadata_json or "{}")
    if not isinstance(merged_metadata, dict):
        merged_metadata = {}
    if isinstance(metadata, dict):
        merged_metadata.update(metadata)
    return json.dumps(merged_metadata, ensure_ascii=False, sort_keys=True)


def build_updates_from_payload(existing, payload):
    metadata = payload.get("metadata")
    updates = {
        "external_title": normalize_text(payload.get("external_title")) or existing["external_title"],
        "naudoc_url": normalize_naudoc_url(payload.get("naudoc_url")) if "naudoc_url" in payload else existing["naudoc_url"],
        "naudoc_title": normalize_text(payload.get("naudoc_title")) if "naudoc_title" in payload else existing["naudoc_title"],
        "sync_status": normalize_text(payload.get("sync_status")) or existing["sync_status"],
        "notes": normalize_text(payload.get("notes")) if "notes" in payload else existing["notes"],
    }
    metadata_json = merge_metadata_json(existing["metadata_json"], metadata)
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


def get_link_by_id(conn, link_id):
    return conn.execute("SELECT * FROM document_links WHERE id = ?", (link_id,)).fetchone()


def relink_document_link(conn, link_id, payload):
    existing = get_link_by_id(conn, link_id)
    if existing is None:
        return None, {"error": "Link not found"}, 404

    external_system = normalize_text(payload.get("external_system")) or existing["external_system"]
    external_entity = normalize_text(payload.get("external_entity")) or existing["external_entity"]
    external_item_id = normalize_text(payload.get("external_item_id")) or existing["external_item_id"]
    external_title = normalize_text(payload.get("external_title")) or existing["external_title"]
    notes = normalize_text(payload.get("notes")) if "notes" in payload else existing["notes"]
    metadata_json = merge_metadata_json(existing["metadata_json"], payload.get("metadata"))

    missing = []
    if not external_system:
        missing.append("external_system")
    if not external_entity:
        missing.append("external_entity")
    if not external_item_id:
        missing.append("external_item_id")
    if not external_title:
        missing.append("external_title")
    if missing:
        return None, {"error": "Missing required fields", "fields": missing}, 400

    conflict = get_link_by_external_key(conn, external_system, external_entity, external_item_id)
    if conflict is not None and int(conflict["id"]) != int(link_id):
        return None, {
            "error": "Another link already exists for this external record",
            "conflict_link_id": int(conflict["id"]),
            "external_system": external_system,
            "external_entity": external_entity,
            "external_item_id": external_item_id,
        }, 409

    old_external_system = existing["external_system"]
    old_external_entity = existing["external_entity"]
    old_external_item_id = existing["external_item_id"]
    now = utcnow_iso()

    conn.execute(
        """
        UPDATE document_links
        SET external_system = ?,
            external_entity = ?,
            external_item_id = ?,
            external_title = ?,
            notes = ?,
            metadata_json = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            external_system,
            external_entity,
            external_item_id,
            external_title,
            notes,
            metadata_json,
            now,
            link_id,
        ),
    )
    conn.execute(
        """
        UPDATE sync_failures
        SET link_id = ?,
            external_system = ?,
            external_entity = ?,
            external_item_id = ?,
            updated_at = ?
        WHERE link_id = ?
           OR (
               external_system = ?
               AND external_entity = ?
               AND external_item_id = ?
           )
        """,
        (
            link_id,
            external_system,
            external_entity,
            external_item_id,
            now,
            link_id,
            old_external_system,
            old_external_entity,
            old_external_item_id,
        ),
    )
    return get_link_by_id(conn, link_id), None, 200


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


def fetch_failure_summary(conn):
    return conn.execute(
        """
        SELECT
            COUNT(*) AS total_count,
            COALESCE(SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END), 0) AS open_count,
            COALESCE(SUM(CASE WHEN status = 'retry_failed' THEN 1 ELSE 0 END), 0) AS retry_failed_count,
            COALESCE(SUM(CASE WHEN status = 'retry_requested' THEN 1 ELSE 0 END), 0) AS retry_requested_count,
            COALESCE(SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END), 0) AS resolved_count
        FROM sync_failures
        """
    ).fetchone()


def fetch_user_profile_summary(conn):
    return conn.execute(
        """
        SELECT
            COUNT(*) AS total_count,
            COALESCE(SUM(CASE WHEN sync_status = 'matched' THEN 1 ELSE 0 END), 0) AS matched_count,
            COALESCE(SUM(CASE WHEN sync_status = 'manual_match' THEN 1 ELSE 0 END), 0) AS manual_match_count,
            COALESCE(SUM(CASE WHEN sync_status = 'needs_review' THEN 1 ELSE 0 END), 0) AS needs_review_count,
            COALESCE(SUM(CASE WHEN sync_status = 'unmatched' THEN 1 ELSE 0 END), 0) AS unmatched_count
        FROM user_directory_profiles
        """
    ).fetchone()


def fetch_identity_source_summary(conn):
    return conn.execute(
        """
        SELECT
            COUNT(*) AS total_count,
            COALESCE(SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END), 0) AS active_count,
            COALESCE(SUM(CASE WHEN is_active = 1 AND provider_type = 'ldap' THEN 1 ELSE 0 END), 0) AS ldap_active_count,
            COALESCE(SUM(CASE WHEN is_default = 1 THEN 1 ELSE 0 END), 0) AS default_count
        FROM identity_sources
        """
    ).fetchone()


def fetch_hospital_role_mapping_summary(conn):
    return conn.execute(
        """
        SELECT
            COUNT(*) AS total_count,
            COALESCE(SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END), 0) AS active_count,
            COALESCE(COUNT(DISTINCT CASE WHEN is_active = 1 THEN hospital_role_key END), 0) AS hospital_role_count
        FROM hospital_role_mappings
        """
    ).fetchone()


def fetch_document_route_definition_summary(conn):
    return conn.execute(
        """
        SELECT
            COUNT(*) AS total_count,
            COALESCE(SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END), 0) AS active_count,
            COALESCE(SUM(CASE WHEN requires_registration = 1 AND is_active = 1 THEN 1 ELSE 0 END), 0) AS registration_count,
            COALESCE(SUM(CASE WHEN requires_approval = 1 AND is_active = 1 THEN 1 ELSE 0 END), 0) AS approval_count
        FROM document_route_definitions
        """
    ).fetchone()


def parse_json_object(value):
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def identity_source_metadata(source):
    return parse_json_object(source.get("metadata_json") if isinstance(source, dict) else source["metadata_json"])


def resolve_secret_from_env(env_key):
    env_key = normalize_text(env_key)
    if not env_key:
        return ""
    return os.environ.get(env_key, "")


def update_identity_source_runtime_fields(conn, source_id, fields):
    if not fields:
        return fetch_table_row_by_id(conn, "identity_sources", source_id)

    assignments = ", ".join(f"{field_name} = ?" for field_name in fields.keys())
    values = tuple(fields.values()) + (source_id,)
    conn.execute(f"UPDATE identity_sources SET {assignments} WHERE id = ?", values)
    return fetch_table_row_by_id(conn, "identity_sources", source_id)


def mark_identity_source_check_result(conn, source_id, status, message):
    now = utcnow_iso()
    return update_identity_source_runtime_fields(
        conn,
        source_id,
        {
            "last_check_at": now,
            "last_check_status": normalize_text(status),
            "last_check_message": normalize_text(message),
            "updated_at": now,
        },
    )


def mark_identity_source_sync_result(conn, source_id, status, message, synced_count=0):
    now = utcnow_iso()
    return update_identity_source_runtime_fields(
        conn,
        source_id,
        {
            "last_sync_at": now,
            "last_sync_status": normalize_text(status),
            "last_sync_message": normalize_text(message),
            "last_synced_count": normalize_int(synced_count) or 0,
            "updated_at": now,
        },
    )


def first_directory_value(payload, attribute_name):
    if not attribute_name:
        return ""
    raw_value = payload.get(attribute_name)
    if isinstance(raw_value, (list, tuple)):
        raw_value = raw_value[0] if raw_value else ""
    return normalize_text(raw_value)


def default_ldap_port(ssl_mode):
    return 636 if normalize_text(ssl_mode) == "ldaps" else 389


def connect_ldap_source(source):
    if not LDAP3_AVAILABLE:
        return None, "ldap3 is not installed"

    host = normalize_text(source["host"])
    if not host:
        return None, "Host is not configured"

    ssl_mode = normalize_text(source["ssl_mode"]) or "none"
    use_ssl = ssl_mode == "ldaps"
    tls_config = Tls(validate=ssl.CERT_NONE) if use_ssl else None
    port = normalize_int(source["port"]) or default_ldap_port(ssl_mode)
    bind_dn = normalize_text(source["bind_dn"])
    password = resolve_secret_from_env(source["bind_password_env_key"])

    try:
        server = Server(
            host,
            port=port,
            use_ssl=use_ssl,
            connect_timeout=LDAP_REQUEST_TIMEOUT,
            tls=tls_config,
        )
        auto_bind = AUTO_BIND_TLS_BEFORE_BIND if ssl_mode == "starttls" else AUTO_BIND_NO_TLS
        connection = Connection(
            server,
            user=bind_dn or None,
            password=password or None,
            auto_bind=auto_bind,
            receive_timeout=LDAP_REQUEST_TIMEOUT,
        )
        return connection, None
    except Exception as exc:
        return None, str(exc)


def test_identity_source_provider(source):
    provider_type = normalize_text(source["provider_type"])
    if provider_type != "ldap":
        return {
            "ok": False,
            "status": "unsupported",
            "message": f"Provider {provider_type or 'unknown'} is not supported for runtime checks",
        }

    connection, error = connect_ldap_source(source)
    if error:
        return {"ok": False, "status": "error", "message": error}

    try:
        base_dn = normalize_text(source["user_base_dn"]) or normalize_text(source["base_dn"])
        if base_dn:
            connection.search(
                search_base=base_dn,
                search_filter="(objectClass=*)",
                search_scope=SUBTREE,
                attributes=[],
                size_limit=1,
            )
        return {
            "ok": True,
            "status": "ok",
            "message": f"LDAP bind successful for {normalize_text(source['source_label']) or normalize_text(source['source_key'])}",
        }
    except Exception as exc:
        return {"ok": False, "status": "error", "message": str(exc)}
    finally:
        try:
            connection.unbind()
        except Exception:
            pass


def unique_profile_match(rows):
    return rows[0] if len(rows) == 1 else None


def lookup_profile_suggestion(conn, username, email, *, exclude_profile_id=None):
    username = normalize_text(username)
    email = normalize_lower(email)

    if username:
        where = """
            (source_username = ? OR linked_username = ?)
        """
        values = [username, username]
        if exclude_profile_id is not None:
            where += " AND id != ?"
            values.append(exclude_profile_id)
        rows = conn.execute(
            f"""
            SELECT *
            FROM user_directory_profiles
            WHERE {where}
            ORDER BY id ASC
            LIMIT 2
            """,
            tuple(values),
        ).fetchall()
        matched_row = unique_profile_match(rows)
        if matched_row is not None:
            return matched_row, "username"

    if email:
        where = """
            (lower(source_email) = ? OR lower(linked_email) = ?)
        """
        values = [email, email]
        if exclude_profile_id is not None:
            where += " AND id != ?"
            values.append(exclude_profile_id)
        rows = conn.execute(
            f"""
            SELECT *
            FROM user_directory_profiles
            WHERE {where}
            ORDER BY id ASC
            LIMIT 2
            """,
            tuple(values),
        ).fetchall()
        matched_row = unique_profile_match(rows)
        if matched_row is not None:
            return matched_row, "email"

    return None, ""


def build_profile_link_payload_from_suggestion(row):
    linked_username = normalize_text(row["linked_username"])
    linked_user_id = normalize_text(row["linked_user_id"])
    linked_display_name = normalize_text(row["linked_display_name"])
    linked_email = normalize_text(row["linked_email"])
    linked_department = normalize_text(row["linked_department"])
    linked_role_key = normalize_text(row["linked_role_key"])
    linked_role_label = normalize_text(row["linked_role_label"])

    if not linked_username and not linked_user_id and normalize_text(row["source_system"]) == "rukovoditel":
        linked_username = normalize_text(row["source_username"])
        linked_display_name = linked_display_name or normalize_text(row["source_display_name"])
        linked_email = linked_email or normalize_text(row["source_email"])
        linked_department = linked_department or normalize_text(row["source_department"])
        linked_role_key = linked_role_key or normalize_text(row["source_role_key"])
        linked_role_label = linked_role_label or normalize_text(row["source_role_label"])

    return {
        "linked_system": "rukovoditel" if (linked_username or linked_user_id) else "",
        "linked_user_id": linked_user_id,
        "linked_username": linked_username,
        "linked_display_name": linked_display_name,
        "linked_email": linked_email,
        "linked_department": linked_department,
        "linked_role_key": linked_role_key,
        "linked_role_label": linked_role_label,
    }


def build_directory_profile_url(source, username):
    metadata = identity_source_metadata(source)
    template = normalize_text(metadata.get("profile_url_template"))
    if not template:
        return ""
    return (
        template.replace("{username}", username)
        .replace("{source_key}", normalize_text(source["source_key"]))
    )


def fetch_identity_source_profiles(source):
    provider_type = normalize_text(source["provider_type"])
    if provider_type != "ldap":
        return None, f"Provider {provider_type or 'unknown'} is not supported for sync"

    connection, error = connect_ldap_source(source)
    if error:
        return None, error

    metadata = identity_source_metadata(source)
    search_base = normalize_text(source["user_base_dn"]) or normalize_text(source["base_dn"])
    if not search_base:
        return None, "user_base_dn or base_dn must be configured"

    search_filter = normalize_text(metadata.get("search_filter")) or "(objectClass=person)"
    sync_limit = normalize_int(metadata.get("sync_limit")) or 100
    attributes = [
        attribute_name
        for attribute_name in {
            normalize_text(source["login_attribute"]),
            normalize_text(source["display_name_attribute"]),
            normalize_text(source["email_attribute"]),
            normalize_text(source["department_attribute"]),
            normalize_text(source["role_attribute"]),
        }
        if attribute_name
    ] or ALL_ATTRIBUTES

    try:
        connection.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=attributes,
            size_limit=sync_limit,
        )
        profiles = []
        for entry in connection.entries:
            entry_payload = entry.entry_attributes_as_dict
            username = first_directory_value(entry_payload, source["login_attribute"])
            if not username:
                continue

            role_value = first_directory_value(entry_payload, source["role_attribute"])
            profiles.append(
                {
                    "username": username,
                    "display_name": first_directory_value(entry_payload, source["display_name_attribute"]),
                    "email": first_directory_value(entry_payload, source["email_attribute"]),
                    "department": first_directory_value(entry_payload, source["department_attribute"]),
                    "role_key": role_value,
                    "role_label": role_value,
                    "profile_url": build_directory_profile_url(source, username),
                    "entry_dn": normalize_text(getattr(entry, "entry_dn", "")),
                }
            )
        return profiles, None
    except Exception as exc:
        return None, str(exc)
    finally:
        try:
            connection.unbind()
        except Exception:
            pass


def sync_identity_source_profiles(conn, source):
    profiles, error = fetch_identity_source_profiles(source)
    if error:
        mark_identity_source_sync_result(conn, source["id"], "error", error, 0)
        return None, {"error": error}

    synced_count = 0
    matched_count = 0
    needs_review_count = 0

    for profile in profiles:
        current_row = conn.execute(
            """
            SELECT *
            FROM user_directory_profiles
            WHERE source_system = ? AND source_username = ?
            LIMIT 1
            """,
            (normalize_text(source["source_system"]) or "ldap", profile["username"]),
        ).fetchone()
        current_profile_id = current_row["id"] if current_row is not None else None
        suggestion_row, match_method = lookup_profile_suggestion(
            conn,
            profile["username"],
            profile["email"],
            exclude_profile_id=current_profile_id,
        )
        metadata = {
            "source": "identity_source_sync",
            "identity_source_key": normalize_text(source["source_key"]),
            "provider_type": normalize_text(source["provider_type"]),
            "entry_dn": profile["entry_dn"],
        }
        link_payload = {
            "linked_system": "",
            "linked_user_id": "",
            "linked_username": "",
            "linked_display_name": "",
            "linked_email": "",
            "linked_department": "",
            "linked_role_key": "",
            "linked_role_label": "",
        }
        sync_status = "unmatched"
        notes = "Профиль импортирован из LDAP."

        if current_row is not None and (normalize_text(current_row["linked_username"]) or normalize_text(current_row["linked_user_id"])):
            link_payload = build_profile_link_payload_from_suggestion(current_row)
            sync_status = normalize_text(current_row["sync_status"]) or "matched"
            metadata["match_method"] = normalize_text(parse_json_object(current_row["metadata_json"]).get("match_method")) or "preserved"
            notes = normalize_text(current_row["notes"]) or "Профиль импортирован из LDAP."
            matched_count += 1

        elif suggestion_row is not None:
            suggestion = build_profile_link_payload_from_suggestion(suggestion_row)
            if suggestion["linked_username"] or suggestion["linked_user_id"]:
                link_payload = suggestion
                sync_status = "matched"
                matched_count += 1
                metadata["match_method"] = f"auto_{match_method}"
                notes = "Профиль автоматически сопоставлен по данным каталога."
            else:
                metadata.update(
                    {
                        "suggested_username": normalize_text(suggestion_row["source_username"]),
                        "suggested_display_name": normalize_text(suggestion_row["source_display_name"]),
                        "suggested_email": normalize_text(suggestion_row["source_email"]),
                        "suggested_department": normalize_text(suggestion_row["source_department"]),
                        "suggested_role_key": normalize_text(suggestion_row["source_role_key"]),
                        "suggested_role_label": normalize_text(suggestion_row["source_role_label"]),
                        "match_method": f"suggested_{match_method}",
                    }
                )
                sync_status = "needs_review"
                needs_review_count += 1

        row, _ = upsert_user_profile(
            conn,
            {
                "source_system": normalize_text(source["source_system"]) or "ldap",
                "source_username": profile["username"],
                "source_display_name": profile["display_name"],
                "source_email": profile["email"],
                "source_department": profile["department"],
                "source_role_key": profile["role_key"],
                "source_role_label": profile["role_label"],
                "source_profile_url": profile["profile_url"],
                "linked_system": link_payload["linked_system"],
                "linked_user_id": link_payload["linked_user_id"],
                "linked_username": link_payload["linked_username"],
                "linked_display_name": link_payload["linked_display_name"],
                "linked_email": link_payload["linked_email"],
                "linked_department": link_payload["linked_department"],
                "linked_role_key": link_payload["linked_role_key"],
                "linked_role_label": link_payload["linked_role_label"],
                "sync_status": sync_status,
                "notes": notes,
                "metadata": metadata,
            },
        )
        if row is not None:
            synced_count += 1

    summary_message = (
        f"Синхронизировано профилей: {synced_count}. "
        f"Автосопоставлено: {matched_count}. "
        f"Требуют проверки: {needs_review_count}."
    )
    mark_identity_source_sync_result(conn, source["id"], "ok", summary_message, synced_count)
    return {
        "synced_count": synced_count,
        "matched_count": matched_count,
        "needs_review_count": needs_review_count,
        "message": summary_message,
    }, None


def build_status_mapping_payload(payload):
    now = utcnow_iso()
    return {
        "match_type": normalize_text(payload.get("match_type")) or "contains",
        "match_value": normalize_text(payload.get("match_value")),
        "request_status_name": normalize_text(payload.get("request_status_name")),
        "doc_status_name": normalize_text(payload.get("doc_status_name")),
        "integration_status_name": normalize_text(payload.get("integration_status_name")),
        "notes": normalize_text(payload.get("notes")),
        "is_active": 1 if normalize_bool(payload.get("is_active"), True) else 0,
        "sort_order": normalize_int(payload.get("sort_order")) or 100,
        "updated_at": now,
        "created_at": now,
    }


def build_field_mapping_payload(payload):
    now = utcnow_iso()
    return {
        "source_system": normalize_text(payload.get("source_system")) or "rukovoditel",
        "source_entity": normalize_text(payload.get("source_entity")),
        "source_field_key": normalize_text(payload.get("source_field_key")),
        "target_system": normalize_text(payload.get("target_system")) or "bridge",
        "target_entity": normalize_text(payload.get("target_entity")) or "metadata",
        "target_field_key": normalize_text(payload.get("target_field_key")),
        "direction": normalize_text(payload.get("direction")) or "push",
        "notes": normalize_text(payload.get("notes")),
        "is_required": 1 if normalize_bool(payload.get("is_required"), False) else 0,
        "is_active": 1 if normalize_bool(payload.get("is_active"), True) else 0,
        "sort_order": normalize_int(payload.get("sort_order")) or 100,
        "updated_at": now,
        "created_at": now,
    }


def validate_status_mapping_payload(payload):
    missing = []
    if not normalize_text(payload.get("match_value")):
        missing.append("match_value")
    match_type = normalize_text(payload.get("match_type")) or "contains"
    if match_type not in {"contains", "exact", "prefix"}:
        return False, {"error": "match_type must be one of contains, exact, prefix"}
    if missing:
        return False, {"error": "Missing required fields", "fields": missing}
    return True, None


def validate_field_mapping_payload(payload):
    missing = []
    for key in ("source_entity", "source_field_key", "target_field_key"):
        if not normalize_text(payload.get(key)):
            missing.append(key)
    if missing:
        return False, {"error": "Missing required fields", "fields": missing}

    source_system = normalize_text(payload.get("source_system")) or "rukovoditel"
    target_system = normalize_text(payload.get("target_system")) or "bridge"
    target_entity = normalize_text(payload.get("target_entity")) or "metadata"
    direction = normalize_text(payload.get("direction")) or "push"

    if source_system not in {"rukovoditel", "bridge", "naudoc"}:
        return False, {"error": "source_system must be one of rukovoditel, bridge, naudoc"}
    if target_system not in {"bridge", "rukovoditel", "naudoc"}:
        return False, {"error": "target_system must be one of bridge, rukovoditel, naudoc"}
    if direction not in {"push", "pull", "bidirectional"}:
        return False, {"error": "direction must be one of push, pull, bidirectional"}
    if not target_entity:
        return False, {"error": "target_entity is required"}

    return True, None


def build_user_profile_payload(payload):
    now = utcnow_iso()
    linked_user_id = normalize_text(payload.get("linked_user_id"))
    linked_username = normalize_text(payload.get("linked_username"))
    linked_system = normalize_text(payload.get("linked_system"))
    if not linked_system and (linked_user_id or linked_username):
        linked_system = "rukovoditel"

    sync_status = normalize_text(payload.get("sync_status"))
    if not sync_status:
        sync_status = "matched" if (linked_user_id or linked_username) else "unmatched"

    return {
        "source_system": normalize_text(payload.get("source_system")) or "naudoc",
        "source_username": normalize_text(payload.get("source_username")),
        "source_display_name": normalize_text(payload.get("source_display_name")),
        "source_email": normalize_text(payload.get("source_email")),
        "source_department": normalize_text(payload.get("source_department")),
        "source_role_key": normalize_text(payload.get("source_role_key")),
        "source_role_label": normalize_text(payload.get("source_role_label")),
        "source_profile_url": normalize_text(payload.get("source_profile_url")),
        "source_folder_url": normalize_text(payload.get("source_folder_url")),
        "linked_system": linked_system,
        "linked_user_id": linked_user_id,
        "linked_username": linked_username,
        "linked_display_name": normalize_text(payload.get("linked_display_name")),
        "linked_email": normalize_text(payload.get("linked_email")),
        "linked_department": normalize_text(payload.get("linked_department")),
        "linked_role_key": normalize_text(payload.get("linked_role_key")),
        "linked_role_label": normalize_text(payload.get("linked_role_label")),
        "sync_status": sync_status,
        "notes": normalize_text(payload.get("notes")),
        "metadata_json": json.dumps(payload.get("metadata") or {}, ensure_ascii=False, sort_keys=True),
        "created_at": now,
        "updated_at": now,
    }


def build_identity_source_payload(payload):
    now = utcnow_iso()
    return {
        "source_key": normalize_text(payload.get("source_key")),
        "source_label": normalize_text(payload.get("source_label")),
        "provider_type": normalize_text(payload.get("provider_type")) or "manual",
        "source_system": normalize_text(payload.get("source_system")),
        "sync_mode": normalize_text(payload.get("sync_mode")) or "manual",
        "host": normalize_text(payload.get("host")),
        "port": normalize_int(payload.get("port")),
        "ssl_mode": normalize_text(payload.get("ssl_mode")) or "none",
        "base_dn": normalize_text(payload.get("base_dn")),
        "user_base_dn": normalize_text(payload.get("user_base_dn")),
        "group_base_dn": normalize_text(payload.get("group_base_dn")),
        "login_attribute": normalize_text(payload.get("login_attribute")) or "uid",
        "display_name_attribute": normalize_text(payload.get("display_name_attribute")) or "cn",
        "email_attribute": normalize_text(payload.get("email_attribute")) or "mail",
        "department_attribute": normalize_text(payload.get("department_attribute")) or "department",
        "role_attribute": normalize_text(payload.get("role_attribute")) or "title",
        "bind_dn": normalize_text(payload.get("bind_dn")),
        "bind_password_env_key": normalize_text(payload.get("bind_password_env_key")),
        "notes": normalize_text(payload.get("notes")),
        "metadata_json": json.dumps(payload.get("metadata") or {}, ensure_ascii=False, sort_keys=True),
        "is_active": 1 if normalize_bool(payload.get("is_active"), True) else 0,
        "is_default": 1 if normalize_bool(payload.get("is_default"), False) else 0,
        "created_at": now,
        "updated_at": now,
    }


def build_hospital_role_mapping_payload(payload):
    now = utcnow_iso()
    return {
        "source_system": normalize_text(payload.get("source_system")) or "rukovoditel",
        "source_role_key": normalize_text(payload.get("source_role_key")),
        "source_role_label": normalize_text(payload.get("source_role_label")),
        "hospital_role_key": normalize_text(payload.get("hospital_role_key")),
        "hospital_role_label": normalize_text(payload.get("hospital_role_label")),
        "access_scope": normalize_text(payload.get("access_scope")) or "custom",
        "notes": normalize_text(payload.get("notes")),
        "is_active": 1 if normalize_bool(payload.get("is_active"), True) else 0,
        "sort_order": normalize_int(payload.get("sort_order")) or 100,
        "created_at": now,
        "updated_at": now,
    }


def build_document_route_definition_payload(payload):
    now = utcnow_iso()
    return {
        "route_key": normalize_text(payload.get("route_key")),
        "route_label": normalize_text(payload.get("route_label")),
        "route_group": normalize_text(payload.get("route_group")) or "hospital",
        "default_doc_status_name": normalize_text(payload.get("default_doc_status_name")),
        "final_doc_status_name": normalize_text(payload.get("final_doc_status_name")),
        "status_sequence_json": json.dumps(normalize_text_list(payload.get("status_sequence")), ensure_ascii=False),
        "participant_role_keys_json": json.dumps(normalize_text_list(payload.get("participant_role_keys")), ensure_ascii=False),
        "requires_registration": 1 if normalize_bool(payload.get("requires_registration"), False) else 0,
        "requires_approval": 1 if normalize_bool(payload.get("requires_approval"), False) else 0,
        "notes": normalize_text(payload.get("notes")),
        "is_active": 1 if normalize_bool(payload.get("is_active"), True) else 0,
        "sort_order": normalize_int(payload.get("sort_order")) or 100,
        "created_at": now,
        "updated_at": now,
    }


def validate_user_profile_payload(payload):
    missing = []
    for key in ("source_system", "source_username"):
        if not normalize_text(payload.get(key)):
            missing.append(key)
    if missing:
        return False, {"error": "Missing required fields", "fields": missing}
    return True, None


def validate_identity_source_payload(payload):
    missing = []
    for key in ("source_key", "source_label", "source_system"):
        if not normalize_text(payload.get(key)):
            missing.append(key)
    if missing:
        return False, {"error": "Missing required fields", "fields": missing}

    provider_type = normalize_text(payload.get("provider_type")) or "manual"
    sync_mode = normalize_text(payload.get("sync_mode")) or "manual"
    ssl_mode = normalize_text(payload.get("ssl_mode")) or "none"

    if provider_type not in {"local", "external", "ldap", "sso", "manual"}:
        return False, {"error": "provider_type must be one of local, external, ldap, sso, manual"}
    if sync_mode not in {"manual", "pull", "push", "sso"}:
        return False, {"error": "sync_mode must be one of manual, pull, push, sso"}
    if ssl_mode not in {"none", "http", "https", "ldap", "starttls", "ldaps"}:
        return False, {"error": "ssl_mode must be one of none, http, https, ldap, starttls, ldaps"}
    return True, None


def validate_hospital_role_mapping_payload(payload):
    missing = []
    for key in ("source_system", "hospital_role_key", "hospital_role_label"):
        if not normalize_text(payload.get(key)):
            missing.append(key)
    if missing:
        return False, {"error": "Missing required fields", "fields": missing}
    if not normalize_text(payload.get("source_role_key")) and not normalize_text(payload.get("source_role_label")):
        return False, {"error": "source_role_key or source_role_label is required"}

    access_scope = normalize_text(payload.get("access_scope")) or "custom"
    if access_scope not in {"full", "department", "own", "registry", "office", "custom"}:
        return False, {"error": "access_scope must be one of full, department, own, registry, office, custom"}
    return True, None


def validate_document_route_definition_payload(payload):
    missing = []
    for key in ("route_key", "route_label"):
        if not normalize_text(payload.get(key)):
            missing.append(key)
    if missing:
        return False, {"error": "Missing required fields", "fields": missing}

    status_sequence = normalize_text_list(payload.get("status_sequence"))
    if not status_sequence:
        return False, {"error": "status_sequence must contain at least one status"}

    route_group = normalize_text(payload.get("route_group")) or "hospital"
    if route_group not in {"hospital", "office", "clinical", "custom"}:
        return False, {"error": "route_group must be one of hospital, office, clinical, custom"}

    return True, None


def create_status_mapping(conn, payload):
    return create_configured_row(
        conn,
        "sync_status_mappings",
        STATUS_MAPPING_DB_FIELDS,
        build_status_mapping_payload,
        payload,
    )


def create_field_mapping(conn, payload):
    return create_configured_row(
        conn,
        "sync_field_mappings",
        FIELD_MAPPING_DB_FIELDS,
        build_field_mapping_payload,
        payload,
    )


def create_identity_source(conn, payload):
    return create_configured_row(
        conn,
        "identity_sources",
        IDENTITY_SOURCE_DB_FIELDS,
        build_identity_source_payload,
        payload,
        unique_default_field="is_default",
    )


def create_hospital_role_mapping(conn, payload):
    return create_configured_row(
        conn,
        "hospital_role_mappings",
        HOSPITAL_ROLE_MAPPING_DB_FIELDS,
        build_hospital_role_mapping_payload,
        payload,
    )


def create_document_route_definition(conn, payload):
    return create_configured_row(
        conn,
        "document_route_definitions",
        DOCUMENT_ROUTE_DEFINITION_DB_FIELDS,
        build_document_route_definition_payload,
        payload,
    )


def update_status_mapping(conn, mapping_id, payload):
    return update_configured_row(
        conn,
        "sync_status_mappings",
        mapping_id,
        STATUS_MAPPING_DB_FIELDS,
        build_status_mapping_payload,
        payload,
    )


def update_field_mapping(conn, mapping_id, payload):
    return update_configured_row(
        conn,
        "sync_field_mappings",
        mapping_id,
        FIELD_MAPPING_DB_FIELDS,
        build_field_mapping_payload,
        payload,
    )


def update_identity_source(conn, source_id, payload):
    return update_configured_row(
        conn,
        "identity_sources",
        source_id,
        IDENTITY_SOURCE_DB_FIELDS,
        build_identity_source_payload,
        payload,
        unique_default_field="is_default",
    )


def update_hospital_role_mapping(conn, mapping_id, payload):
    return update_configured_row(
        conn,
        "hospital_role_mappings",
        mapping_id,
        HOSPITAL_ROLE_MAPPING_DB_FIELDS,
        build_hospital_role_mapping_payload,
        payload,
    )


def update_document_route_definition(conn, route_definition_id, payload):
    return update_configured_row(
        conn,
        "document_route_definitions",
        route_definition_id,
        DOCUMENT_ROUTE_DEFINITION_DB_FIELDS,
        build_document_route_definition_payload,
        payload,
    )


def enrich_user_profile_item(item, active_hospital_role_rows):
    item["source_hospital_role"] = resolve_hospital_role_mapping(
        active_hospital_role_rows,
        item.get("source_system"),
        item.get("source_role_key"),
        item.get("source_role_label"),
    )
    item["linked_hospital_role"] = resolve_hospital_role_mapping(
        active_hospital_role_rows,
        item.get("linked_system"),
        item.get("linked_role_key"),
        item.get("linked_role_label"),
    )
    return item


def build_enriched_user_profiles(rows, active_hospital_role_rows):
    return [
        enrich_user_profile_item(user_profile_row_to_dict(row), active_hospital_role_rows)
        for row in rows
    ]


def upsert_user_profile(conn, payload):
    data = build_user_profile_payload(payload)
    existing = conn.execute(
        """
        SELECT *
        FROM user_directory_profiles
        WHERE source_system = ? AND source_username = ?
        LIMIT 1
        """,
        (data["source_system"], data["source_username"]),
    ).fetchone()

    if existing is None:
        cursor = conn.execute(
            """
            INSERT INTO user_directory_profiles (
                source_system,
                source_username,
                source_display_name,
                source_email,
                source_department,
                source_role_key,
                source_role_label,
                source_profile_url,
                source_folder_url,
                linked_system,
                linked_user_id,
                linked_username,
                linked_display_name,
                linked_email,
                linked_department,
                linked_role_key,
                linked_role_label,
                sync_status,
                notes,
                metadata_json,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["source_system"],
                data["source_username"],
                data["source_display_name"],
                data["source_email"],
                data["source_department"],
                data["source_role_key"],
                data["source_role_label"],
                data["source_profile_url"],
                data["source_folder_url"],
                data["linked_system"],
                data["linked_user_id"],
                data["linked_username"],
                data["linked_display_name"],
                data["linked_email"],
                data["linked_department"],
                data["linked_role_key"],
                data["linked_role_label"],
                data["sync_status"],
                data["notes"],
                data["metadata_json"],
                data["created_at"],
                data["updated_at"],
            ),
        )
        return conn.execute("SELECT * FROM user_directory_profiles WHERE id = ?", (cursor.lastrowid,)).fetchone(), "created"

    return persist_user_profile_fields(conn, existing["id"], data), "updated"


def update_user_profile(conn, profile_id, payload):
    existing = conn.execute("SELECT * FROM user_directory_profiles WHERE id = ?", (profile_id,)).fetchone()
    if existing is None:
        return None

    data = build_user_profile_payload(
        {
            "source_system": existing["source_system"],
            "source_username": existing["source_username"],
            "source_display_name": payload.get("source_display_name", existing["source_display_name"]),
            "source_email": payload.get("source_email", existing["source_email"]),
            "source_department": payload.get("source_department", existing["source_department"]),
            "source_role_key": payload.get("source_role_key", existing["source_role_key"]),
            "source_role_label": payload.get("source_role_label", existing["source_role_label"]),
            "source_profile_url": payload.get("source_profile_url", existing["source_profile_url"]),
            "source_folder_url": payload.get("source_folder_url", existing["source_folder_url"]),
            "linked_system": payload.get("linked_system", existing["linked_system"]),
            "linked_user_id": payload.get("linked_user_id", existing["linked_user_id"]),
            "linked_username": payload.get("linked_username", existing["linked_username"]),
            "linked_display_name": payload.get("linked_display_name", existing["linked_display_name"]),
            "linked_email": payload.get("linked_email", existing["linked_email"]),
            "linked_department": payload.get("linked_department", existing["linked_department"]),
            "linked_role_key": payload.get("linked_role_key", existing["linked_role_key"]),
            "linked_role_label": payload.get("linked_role_label", existing["linked_role_label"]),
            "sync_status": payload.get("sync_status", existing["sync_status"]),
            "notes": payload.get("notes", existing["notes"]),
            "metadata": payload.get("metadata", json.loads(existing["metadata_json"] or "{}")),
        }
    )
    return persist_user_profile_fields(conn, profile_id, data)


STATUS_MAPPING_ROUTE_SPEC = {
    "checkbox_fields": ("is_active",),
    "validator": validate_status_mapping_payload,
    "create_func": create_status_mapping,
    "update_func": update_status_mapping,
    "serializer": status_mapping_row_to_dict,
    "response_key": "mapping",
    "not_found_error": "Mapping not found",
}

FIELD_MAPPING_ROUTE_SPEC = {
    "checkbox_fields": ("is_active", "is_required"),
    "validator": validate_field_mapping_payload,
    "create_func": create_field_mapping,
    "update_func": update_field_mapping,
    "serializer": field_mapping_row_to_dict,
    "response_key": "mapping",
    "not_found_error": "Field mapping not found",
}

IDENTITY_SOURCE_ROUTE_SPEC = {
    "checkbox_fields": ("is_active", "is_default"),
    "validator": validate_identity_source_payload,
    "create_func": create_identity_source,
    "update_func": update_identity_source,
    "serializer": identity_source_row_to_dict,
    "response_key": "identity_source",
    "not_found_error": "Identity source not found",
    "duplicate_error": "Identity source with this source_key already exists",
}

HOSPITAL_ROLE_MAPPING_ROUTE_SPEC = {
    "checkbox_fields": ("is_active",),
    "validator": validate_hospital_role_mapping_payload,
    "create_func": create_hospital_role_mapping,
    "update_func": update_hospital_role_mapping,
    "serializer": hospital_role_mapping_row_to_dict,
    "response_key": "mapping",
    "not_found_error": "Hospital role mapping not found",
    "duplicate_error": "Hospital role mapping already exists",
}

DOCUMENT_ROUTE_DEFINITION_ROUTE_SPEC = {
    "checkbox_fields": ("is_active", "requires_registration", "requires_approval"),
    "validator": validate_document_route_definition_payload,
    "create_func": create_document_route_definition,
    "update_func": update_document_route_definition,
    "serializer": document_route_definition_row_to_dict,
    "response_key": "route_definition",
    "not_found_error": "Document route definition not found",
    "duplicate_error": "Document route definition already exists",
}


def parse_model_payload(checkbox_fields=()):
    payload, error_response = parse_payload()
    if error_response:
        return None, error_response
    apply_form_checkbox_fields(payload, checkbox_fields)
    return payload, None


def handle_create_model_route(spec):
    payload, error_response = parse_model_payload(spec.get("checkbox_fields", ()))
    if error_response:
        return error_response

    valid, error = spec["validator"](payload)
    if not valid:
        return jsonify(error), 400

    try:
        with closing(db_connection()) as conn:
            row = spec["create_func"](conn, payload)
            conn.commit()
    except sqlite3.IntegrityError:
        duplicate_error = spec.get("duplicate_error")
        if duplicate_error:
            return jsonify({"error": duplicate_error}), 409
        raise

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "created", spec["response_key"]: spec["serializer"](row)}), 201


def handle_update_model_route(row_id, spec):
    payload, error_response = parse_model_payload(spec.get("checkbox_fields", ()))
    if error_response:
        return error_response

    valid, error = spec["validator"](payload)
    if not valid:
        return jsonify(error), 400

    try:
        with closing(db_connection()) as conn:
            row = spec["update_func"](conn, row_id, payload)
            if row is None:
                return jsonify({"error": spec["not_found_error"]}), 404
            conn.commit()
    except sqlite3.IntegrityError:
        duplicate_error = spec.get("duplicate_error")
        if duplicate_error:
            return jsonify({"error": duplicate_error}), 409
        raise

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "updated", spec["response_key"]: spec["serializer"](row)})


def accept_user_profile_suggestion(conn, profile_id):
    existing = conn.execute("SELECT * FROM user_directory_profiles WHERE id = ?", (profile_id,)).fetchone()
    if existing is None:
        return None, {"error": "User profile not found"}

    metadata = json.loads(existing["metadata_json"] or "{}")
    suggested_username = normalize_text(metadata.get("suggested_username"))
    suggested_user_id = normalize_text(metadata.get("suggested_user_id"))

    if not suggested_username and not suggested_user_id:
        return None, {"error": "Suggested match is missing"}

    metadata["accepted_suggestion_at"] = utcnow_iso()
    metadata["match_method"] = metadata.get("match_method") or "manual_accept"

    row = update_user_profile(
        conn,
        profile_id,
        {
            "linked_system": "rukovoditel",
            "linked_user_id": suggested_user_id,
            "linked_username": suggested_username,
            "linked_display_name": metadata.get("suggested_display_name", existing["linked_display_name"]),
            "linked_email": metadata.get("suggested_email", existing["linked_email"]),
            "linked_department": metadata.get("suggested_department", existing["linked_department"]),
            "linked_role_key": metadata.get("suggested_role_key", existing["linked_role_key"]),
            "linked_role_label": metadata.get("suggested_role_label", existing["linked_role_label"]),
            "sync_status": "matched",
            "notes": "Профиль подтвержден по подсказке Bridge.",
            "metadata": metadata,
        },
    )
    return row, None


def fetch_active_hospital_role_mappings(conn):
    return conn.execute(
        """
        SELECT *
        FROM hospital_role_mappings
        WHERE is_active = 1
        ORDER BY sort_order ASC, id ASC
        """
    ).fetchall()


def resolve_hospital_role_mapping(role_mapping_rows, source_system, role_key, role_label):
    source_system_normalized = normalize_lower(source_system)
    role_key_normalized = normalize_lower(role_key)
    role_label_normalized = normalize_lower(role_label)

    for row in role_mapping_rows:
        if normalize_lower(row["source_system"]) != source_system_normalized:
            continue
        mapping_key = normalize_lower(row["source_role_key"])
        mapping_label = normalize_lower(row["source_role_label"])
        key_matches = bool(mapping_key and mapping_key == role_key_normalized)
        label_matches = bool(mapping_label and mapping_label == role_label_normalized)
        if key_matches or label_matches:
            return hospital_role_mapping_row_to_dict(row)
    return None


def fetch_active_document_route_definitions(conn):
    return conn.execute(
        """
        SELECT *
        FROM document_route_definitions
        WHERE is_active = 1
        ORDER BY sort_order ASC, id ASC
        """
    ).fetchall()


def resolve_document_route_definition(route_definition_rows, route_label, route_key=""):
    route_label_normalized = normalize_lower(route_label)
    route_key_normalized = normalize_lower(route_key)

    for row in route_definition_rows:
        if route_key_normalized and normalize_lower(row["route_key"]) == route_key_normalized:
            return document_route_definition_row_to_dict(row)
        if route_label_normalized and normalize_lower(row["route_label"]) == route_label_normalized:
            return document_route_definition_row_to_dict(row)
    return None


def build_failure_payload(payload):
    now = utcnow_iso()
    return {
        "source": normalize_text(payload.get("source")) or "bridge",
        "job_name": normalize_text(payload.get("job_name")),
        "external_system": normalize_text(payload.get("external_system")),
        "external_entity": normalize_text(payload.get("external_entity")),
        "external_item_id": normalize_text(payload.get("external_item_id")),
        "link_id": normalize_int(payload.get("link_id")) or None,
        "message": normalize_text(payload.get("message")),
        "context_json": json.dumps(payload.get("context") or {}, ensure_ascii=False, sort_keys=True),
        "status": normalize_text(payload.get("status")) or "open",
        "created_at": now,
        "updated_at": now,
    }


def validate_failure_payload(payload):
    missing = []
    if not normalize_text(payload.get("job_name")):
        missing.append("job_name")
    if not normalize_text(payload.get("message")):
        missing.append("message")
    if missing:
        return False, {"error": "Missing required fields", "fields": missing}
    return True, None


def upsert_sync_failure(conn, payload):
    data = build_failure_payload(payload)
    existing = conn.execute(
        """
        SELECT *
        FROM sync_failures
        WHERE source = ?
          AND job_name = ?
          AND external_system = ?
          AND external_entity = ?
          AND external_item_id = ?
          AND status IN ('open', 'retry_requested', 'retry_failed')
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            data["source"],
            data["job_name"],
            data["external_system"],
            data["external_entity"],
            data["external_item_id"],
        ),
    ).fetchone()

    if existing is None:
        cursor = conn.execute(
            """
            INSERT INTO sync_failures (
                source,
                job_name,
                external_system,
                external_entity,
                external_item_id,
                link_id,
                message,
                context_json,
                status,
                retry_count,
                last_retry_at,
                last_result_json,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, '', '{}', ?, ?)
            """,
            (
                data["source"],
                data["job_name"],
                data["external_system"],
                data["external_entity"],
                data["external_item_id"],
                data["link_id"],
                data["message"],
                data["context_json"],
                data["status"],
                data["created_at"],
                data["updated_at"],
            ),
        )
        row = conn.execute("SELECT * FROM sync_failures WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return row, "created"

    conn.execute(
        """
        UPDATE sync_failures
        SET link_id = ?,
            message = ?,
            context_json = ?,
            status = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            data["link_id"],
            data["message"],
            data["context_json"],
            "open",
            data["updated_at"],
            existing["id"],
        ),
    )
    row = conn.execute("SELECT * FROM sync_failures WHERE id = ?", (existing["id"],)).fetchone()
    return row, "updated"


def resolve_sync_failures(conn, payload):
    source = normalize_text(payload.get("source"))
    job_name = normalize_text(payload.get("job_name"))
    external_system = normalize_text(payload.get("external_system"))
    external_entity = normalize_text(payload.get("external_entity"))
    external_item_id = normalize_text(payload.get("external_item_id"))
    link_id = normalize_int(payload.get("link_id"))

    if not source or not job_name:
        return 0

    where = ["source = ?", "job_name = ?", "status != 'resolved'"]
    values = [source, job_name]

    if external_system:
        where.append("external_system = ?")
        values.append(external_system)
    if external_entity:
        where.append("external_entity = ?")
        values.append(external_entity)
    if external_item_id:
        where.append("external_item_id = ?")
        values.append(external_item_id)
    if link_id:
        where.append("link_id = ?")
        values.append(link_id)

    if len(where) <= 3:
        return 0

    update_values = [utcnow_iso(), json.dumps(payload.get("result") or {}, ensure_ascii=False, sort_keys=True)]
    cursor = conn.execute(
        f"""
        UPDATE sync_failures
        SET status = 'resolved',
            updated_at = ?,
            last_result_json = ?
        WHERE {' AND '.join(where)}
        """,
        update_values + values,
    )
    return cursor.rowcount


def build_retry_payload(failure):
    context = json.loads(failure["context_json"] or "{}")
    job_name = failure["job_name"]
    payload = {"job": job_name}

    external_item_id = normalize_int(failure["external_item_id"])
    external_entity = normalize_text(failure["external_entity"])

    if job_name == "service_requests":
        payload["request_id"] = external_item_id or normalize_int(context.get("request_id"))
    elif job_name == "projects":
        payload["project_id"] = external_item_id or normalize_int(context.get("project_id"))
    elif job_name == "pull_bridge":
        if external_entity == "service_requests":
            payload["request_id"] = external_item_id or normalize_int(context.get("request_id"))
        elif external_entity == "projects":
            payload["project_id"] = external_item_id or normalize_int(context.get("project_id"))
        elif external_entity == "document_cards":
            payload["doc_card_id"] = external_item_id or normalize_int(context.get("doc_card_id"))

    return {key: value for key, value in payload.items() if value not in ("", 0, None)}


def retry_sync_failure(conn, failure):
    if not SYNC_CONTROL_TOKEN:
        return False, {"error": "SYNC_CONTROL_TOKEN is not configured"}

    payload = build_retry_payload(failure)
    if "job" not in payload:
        return False, {"error": "Retry payload is incomplete"}

    try:
        response = requests.post(
            SYNC_CONTROL_URL,
            json=payload,
            headers={"X-Sync-Control-Token": SYNC_CONTROL_TOKEN},
            timeout=max(REQUEST_TIMEOUT, 30),
        )
        result = response.json() if response.text.strip() else {}
    except requests.RequestException as exc:
        result = {"error": str(exc)}
        ok = False
    except ValueError:
        result = {"error": "Sync control response is not valid JSON", "body": response.text}
        ok = False
    else:
        ok = response.ok and result.get("status") == "ok"

    status = "resolved" if ok else "retry_failed"
    now = utcnow_iso()
    conn.execute(
        """
        UPDATE sync_failures
        SET status = ?,
            retry_count = retry_count + 1,
            last_retry_at = ?,
            last_result_json = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            status,
            now,
            json.dumps(result, ensure_ascii=False, sort_keys=True),
            now,
            failure["id"],
        ),
    )
    row = conn.execute("SELECT * FROM sync_failures WHERE id = ?", (failure["id"],)).fetchone()
    return ok, failure_row_to_dict(row)


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
        failure_rows = conn.execute(
            """
            SELECT *
            FROM sync_failures
            WHERE status != 'resolved'
            ORDER BY updated_at DESC, id DESC
            LIMIT 20
            """
        ).fetchall()
        failure_summary = fetch_failure_summary(conn)
        mapping_rows = conn.execute(
            """
            SELECT *
            FROM sync_status_mappings
            ORDER BY sort_order ASC, id ASC
            """
        ).fetchall()
        field_mapping_rows = conn.execute(
            """
            SELECT *
            FROM sync_field_mappings
            ORDER BY source_entity ASC, sort_order ASC, id ASC
            """
        ).fetchall()
        user_profile_rows = conn.execute(
            """
            SELECT *
            FROM user_directory_profiles
            ORDER BY
                CASE WHEN sync_status = 'matched' THEN 1 ELSE 0 END ASC,
                source_system ASC,
                source_username ASC
            """
        ).fetchall()
        user_profile_summary = fetch_user_profile_summary(conn)
        identity_source_rows = conn.execute(
            """
            SELECT *
            FROM identity_sources
            ORDER BY is_default DESC, is_active DESC, source_label ASC, id ASC
            """
        ).fetchall()
        identity_source_summary = fetch_identity_source_summary(conn)
        hospital_role_mapping_rows = conn.execute(
            """
            SELECT *
            FROM hospital_role_mappings
            ORDER BY source_system ASC, sort_order ASC, id ASC
            """
        ).fetchall()
        hospital_role_summary = fetch_hospital_role_mapping_summary(conn)
        document_route_definition_rows = conn.execute(
            """
            SELECT *
            FROM document_route_definitions
            ORDER BY route_group ASC, sort_order ASC, id ASC
            """
        ).fetchall()
        document_route_summary = fetch_document_route_definition_summary(conn)
        active_hospital_role_rows = [row for row in hospital_role_mapping_rows if row["is_active"]]

    user_profiles = build_enriched_user_profiles(user_profile_rows, active_hospital_role_rows)
    return render_template(
        "index.html",
        app_title=APP_TITLE,
        naudoc_url=NAUDOC_PUBLIC_URL,
        rukovoditel_url=RUKOVODITEL_PUBLIC_URL,
        sync_control_enabled=bool(SYNC_CONTROL_TOKEN and SYNC_CONTROL_URL),
        links=[row_to_dict(row) for row in rows],
        attention_links=[row_to_dict(row) for row in attention_rows],
        sync_failures=[failure_row_to_dict(row) for row in failure_rows],
        status_mappings=[status_mapping_row_to_dict(row) for row in mapping_rows],
        field_mappings=[field_mapping_row_to_dict(row) for row in field_mapping_rows],
        selected_filters=selected_filters,
        summary_counts=dict(summary),
        failure_summary=dict(failure_summary),
        user_profiles=user_profiles,
        user_profile_summary=dict(user_profile_summary),
        identity_sources=[identity_source_row_to_dict(row) for row in identity_source_rows],
        identity_source_summary=dict(identity_source_summary),
        hospital_role_mappings=[hospital_role_mapping_row_to_dict(row) for row in hospital_role_mapping_rows],
        hospital_role_summary=dict(hospital_role_summary),
        document_route_definitions=[document_route_definition_row_to_dict(row) for row in document_route_definition_rows],
        document_route_summary=dict(document_route_summary),
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


@app.post("/links/<int:link_id>/relink")
def relink_link_route(link_id):
    payload, error_response = parse_payload()
    if error_response:
        return error_response

    with closing(db_connection()) as conn:
        row, error, status_code = relink_document_link(conn, link_id, payload)
        if error is not None:
            return jsonify(error), status_code
        conn.commit()

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "relinked", "link": row_to_dict(row)})


@app.post("/links/<int:link_id>/writeback")
def writeback_link_route(link_id):
    try:
        with closing(db_connection()) as conn:
            row, result = writeback_link_to_naudoc(conn, link_id)
            conn.commit()
    except requests.RequestException as exc:
        return jsonify({"error": f"NauDoc write-back request failed: {exc}"}), 502
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 400

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "ok", "link": row, "writeback": result})


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


@app.get("/status-mappings")
def list_status_mappings():
    active_only = normalize_bool(request.args.get("active"), False)
    sql = "SELECT * FROM sync_status_mappings"
    values = []
    if active_only:
        sql += " WHERE is_active = ?"
        values.append(1)
    sql += " ORDER BY sort_order ASC, id ASC"

    with closing(db_connection()) as conn:
        rows = conn.execute(sql, values).fetchall()
    return jsonify([status_mapping_row_to_dict(row) for row in rows])


@app.get("/field-mappings")
def list_field_mappings():
    sql = "SELECT * FROM sync_field_mappings"
    values = []
    where = []

    source_entity = normalize_text(request.args.get("source_entity"))
    source_system = normalize_text(request.args.get("source_system"))
    target_system = normalize_text(request.args.get("target_system"))
    target_entity = normalize_text(request.args.get("target_entity"))
    direction = normalize_text(request.args.get("direction"))
    active_only = normalize_bool(request.args.get("active"), False)

    if source_entity:
        where.append("source_entity = ?")
        values.append(source_entity)
    if source_system:
        where.append("source_system = ?")
        values.append(source_system)
    if target_system:
        where.append("target_system = ?")
        values.append(target_system)
    if target_entity:
        where.append("target_entity = ?")
        values.append(target_entity)
    if direction:
        where.append("direction = ?")
        values.append(direction)
    if active_only:
        where.append("is_active = 1")

    if where:
        sql += " WHERE " + " AND ".join(where)

    sql += " ORDER BY source_entity ASC, sort_order ASC, id ASC"

    with closing(db_connection()) as conn:
        rows = conn.execute(sql, values).fetchall()
    return jsonify([field_mapping_row_to_dict(row) for row in rows])


@app.get("/identity-sources")
def list_identity_sources():
    sql = "SELECT * FROM identity_sources"
    values = []
    where = []

    provider_type = normalize_text(request.args.get("provider_type"))
    source_system = normalize_text(request.args.get("source_system"))
    active_only = normalize_bool(request.args.get("active"), False)

    if provider_type:
        where.append("provider_type = ?")
        values.append(provider_type)
    if source_system:
        where.append("source_system = ?")
        values.append(source_system)
    if active_only:
        where.append("is_active = 1")

    if where:
        sql += " WHERE " + " AND ".join(where)

    sql += " ORDER BY is_default DESC, is_active DESC, source_label ASC, id ASC"

    with closing(db_connection()) as conn:
        rows = conn.execute(sql, values).fetchall()
    return jsonify([identity_source_row_to_dict(row) for row in rows])


@app.get("/hospital-role-mappings")
def list_hospital_role_mappings():
    sql = "SELECT * FROM hospital_role_mappings"
    values = []
    where = []

    source_system = normalize_text(request.args.get("source_system"))
    active_only = normalize_bool(request.args.get("active"), False)

    if source_system:
        where.append("source_system = ?")
        values.append(source_system)
    if active_only:
        where.append("is_active = 1")

    if where:
        sql += " WHERE " + " AND ".join(where)

    sql += " ORDER BY source_system ASC, sort_order ASC, id ASC"

    with closing(db_connection()) as conn:
        rows = conn.execute(sql, values).fetchall()
    return jsonify([hospital_role_mapping_row_to_dict(row) for row in rows])


@app.get("/document-route-definitions")
def list_document_route_definitions():
    sql = "SELECT * FROM document_route_definitions"
    values = []
    where = []

    route_group = normalize_text(request.args.get("route_group"))
    active_only = normalize_bool(request.args.get("active"), False)

    if route_group:
        where.append("route_group = ?")
        values.append(route_group)
    if active_only:
        where.append("is_active = 1")

    if where:
        sql += " WHERE " + " AND ".join(where)

    sql += " ORDER BY route_group ASC, sort_order ASC, id ASC"

    with closing(db_connection()) as conn:
        rows = conn.execute(sql, values).fetchall()
    return jsonify([document_route_definition_row_to_dict(row) for row in rows])


@app.post("/status-mappings")
def create_status_mapping_route():
    return handle_create_model_route(STATUS_MAPPING_ROUTE_SPEC)


@app.post("/field-mappings")
def create_field_mapping_route():
    return handle_create_model_route(FIELD_MAPPING_ROUTE_SPEC)


@app.post("/identity-sources")
def create_identity_source_route():
    return handle_create_model_route(IDENTITY_SOURCE_ROUTE_SPEC)


@app.post("/hospital-role-mappings")
def create_hospital_role_mapping_route():
    return handle_create_model_route(HOSPITAL_ROLE_MAPPING_ROUTE_SPEC)


@app.post("/document-route-definitions")
def create_document_route_definition_route():
    return handle_create_model_route(DOCUMENT_ROUTE_DEFINITION_ROUTE_SPEC)


@app.post("/status-mappings/<int:mapping_id>/update")
def update_status_mapping_route(mapping_id):
    return handle_update_model_route(mapping_id, STATUS_MAPPING_ROUTE_SPEC)


@app.post("/field-mappings/<int:mapping_id>/update")
def update_field_mapping_route(mapping_id):
    return handle_update_model_route(mapping_id, FIELD_MAPPING_ROUTE_SPEC)


@app.post("/identity-sources/<int:source_id>/update")
def update_identity_source_route(source_id):
    return handle_update_model_route(source_id, IDENTITY_SOURCE_ROUTE_SPEC)


@app.post("/hospital-role-mappings/<int:mapping_id>/update")
def update_hospital_role_mapping_route(mapping_id):
    return handle_update_model_route(mapping_id, HOSPITAL_ROLE_MAPPING_ROUTE_SPEC)


@app.post("/document-route-definitions/<int:route_definition_id>/update")
def update_document_route_definition_route(route_definition_id):
    return handle_update_model_route(route_definition_id, DOCUMENT_ROUTE_DEFINITION_ROUTE_SPEC)


@app.post("/identity-sources/<int:source_id>/test")
def test_identity_source_route(source_id):
    with closing(db_connection()) as conn:
        source = fetch_table_row_by_id(conn, "identity_sources", source_id)
        if source is None:
            return jsonify({"error": "Identity source not found"}), 404

        result = test_identity_source_provider(source)
        mark_identity_source_check_result(conn, source_id, result["status"], result["message"])
        conn.commit()

    status_code = 200 if result["ok"] else (400 if result["status"] == "unsupported" else 502)
    if request.form:
        return redirect(url_for("index"))
    return jsonify(result), status_code


@app.post("/identity-sources/<int:source_id>/sync")
def sync_identity_source_route(source_id):
    with closing(db_connection()) as conn:
        source = fetch_table_row_by_id(conn, "identity_sources", source_id)
        if source is None:
            return jsonify({"error": "Identity source not found"}), 404

        summary, error = sync_identity_source_profiles(conn, source)
        conn.commit()

    if error:
        status_code = 400 if "not supported" in error["error"] else 502
        if request.form:
            return redirect(url_for("index"))
        return jsonify(error), status_code

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "ok", **summary})


@app.post("/status-mappings/<int:mapping_id>/delete")
def delete_status_mapping_route(mapping_id):
    with closing(db_connection()) as conn:
        cursor = conn.execute("DELETE FROM sync_status_mappings WHERE id = ?", (mapping_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Mapping not found"}), 404

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "deleted", "id": mapping_id})


@app.post("/field-mappings/<int:mapping_id>/delete")
def delete_field_mapping_route(mapping_id):
    with closing(db_connection()) as conn:
        cursor = conn.execute("DELETE FROM sync_field_mappings WHERE id = ?", (mapping_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Field mapping not found"}), 404

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "deleted", "id": mapping_id})


@app.post("/identity-sources/<int:source_id>/delete")
def delete_identity_source_route(source_id):
    with closing(db_connection()) as conn:
        cursor = conn.execute("DELETE FROM identity_sources WHERE id = ?", (source_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Identity source not found"}), 404

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "deleted", "id": source_id})


@app.post("/hospital-role-mappings/<int:mapping_id>/delete")
def delete_hospital_role_mapping_route(mapping_id):
    with closing(db_connection()) as conn:
        cursor = conn.execute("DELETE FROM hospital_role_mappings WHERE id = ?", (mapping_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Hospital role mapping not found"}), 404

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "deleted", "id": mapping_id})


@app.post("/document-route-definitions/<int:route_definition_id>/delete")
def delete_document_route_definition_route(route_definition_id):
    with closing(db_connection()) as conn:
        cursor = conn.execute("DELETE FROM document_route_definitions WHERE id = ?", (route_definition_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Document route definition not found"}), 404

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "deleted", "id": route_definition_id})


@app.get("/sync-failures")
def list_sync_failures():
    status = normalize_text(request.args.get("status"))
    values = []
    sql = "SELECT * FROM sync_failures"
    where = []
    if status:
        where.append("status = ?")
        values.append(status)
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY updated_at DESC, id DESC"

    with closing(db_connection()) as conn:
        rows = conn.execute(sql, values).fetchall()
    return jsonify([failure_row_to_dict(row) for row in rows])


@app.get("/user-profiles")
def list_user_profiles():
    sql = "SELECT * FROM user_directory_profiles"
    values = []
    where = []

    source_system = normalize_text(request.args.get("source_system"))
    sync_status = normalize_text(request.args.get("sync_status"))
    source_username = normalize_text(request.args.get("source_username"))

    if source_system:
        where.append("source_system = ?")
        values.append(source_system)
    if sync_status:
        where.append("sync_status = ?")
        values.append(sync_status)
    if source_username:
        where.append("source_username = ?")
        values.append(source_username)

    if where:
        sql += " WHERE " + " AND ".join(where)

    sql += " ORDER BY source_system ASC, source_username ASC"

    with closing(db_connection()) as conn:
        rows = conn.execute(sql, values).fetchall()
        active_hospital_role_rows = fetch_active_hospital_role_mappings(conn)

    payload = build_enriched_user_profiles(rows, active_hospital_role_rows)
    return jsonify(payload)


@app.post("/user-profiles")
@app.post("/user-profiles/upsert")
def upsert_user_profile_route():
    payload, error_response = parse_payload()
    if error_response:
        return error_response
    if request.form:
        payload["sync_status"] = normalize_text(request.form.get("sync_status")) or payload.get("sync_status")

    valid, error = validate_user_profile_payload(payload)
    if not valid:
        return jsonify(error), 400

    with closing(db_connection()) as conn:
        row, action = upsert_user_profile(conn, payload)
        conn.commit()

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": action, "profile": user_profile_row_to_dict(row)}), 201 if action == "created" else 200


@app.post("/user-profiles/<int:profile_id>/update")
def update_user_profile_route(profile_id):
    payload, error_response = parse_payload()
    if error_response:
        return error_response
    if request.form:
        payload["sync_status"] = normalize_text(request.form.get("sync_status")) or payload.get("sync_status")

    with closing(db_connection()) as conn:
        row = update_user_profile(conn, profile_id, payload)
        if row is None:
            return jsonify({"error": "User profile not found"}), 404
        conn.commit()

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "updated", "profile": user_profile_row_to_dict(row)})


@app.post("/user-profiles/<int:profile_id>/accept-suggestion")
def accept_user_profile_suggestion_route(profile_id):
    with closing(db_connection()) as conn:
        row, error = accept_user_profile_suggestion(conn, profile_id)
        if error:
            return jsonify(error), 400 if error.get("error") != "User profile not found" else 404
        conn.commit()

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "matched", "profile": user_profile_row_to_dict(row)})


@app.post("/sync-failures")
def create_sync_failure():
    payload, error_response = parse_payload()
    if error_response:
        return error_response

    valid, error = validate_failure_payload(payload)
    if not valid:
        return jsonify(error), 400

    with closing(db_connection()) as conn:
        row, action = upsert_sync_failure(conn, payload)
        conn.commit()

    return jsonify({"status": action, "failure": failure_row_to_dict(row)}), 201 if action == "created" else 200


@app.post("/sync-failures/resolve")
def resolve_sync_failures_route():
    payload, error_response = parse_payload()
    if error_response:
        return error_response

    with closing(db_connection()) as conn:
        resolved = resolve_sync_failures(conn, payload)
        conn.commit()

    return jsonify({"status": "resolved", "count": resolved})


@app.post("/sync-failures/<int:failure_id>/retry")
def retry_sync_failure_route(failure_id):
    with closing(db_connection()) as conn:
        failure = conn.execute("SELECT * FROM sync_failures WHERE id = ?", (failure_id,)).fetchone()
        if failure is None:
            return jsonify({"error": "Failure not found"}), 404

        ok, result = retry_sync_failure(conn, failure)
        conn.commit()

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "resolved" if ok else "retry_failed", "failure": result}), 200 if ok else 502


@app.post("/sync-failures/<int:failure_id>/resolve")
def resolve_sync_failure_route(failure_id):
    with closing(db_connection()) as conn:
        cursor = conn.execute(
            """
            UPDATE sync_failures
            SET status = 'resolved',
                updated_at = ?
            WHERE id = ?
            """,
            (utcnow_iso(), failure_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Failure not found"}), 404

    if request.form:
        return redirect(url_for("index"))
    return jsonify({"status": "resolved", "id": failure_id})


if __name__ == "__main__":
    ensure_db()
    app.run(host="0.0.0.0", port=8000, debug=False)
