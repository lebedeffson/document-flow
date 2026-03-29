# Closed LAN Go-Live Checklist

Цель: дать короткий и боевой порядок выкладки в закрытой локальной сети больницы, когда у пользователей нет интернета, а платформа должна открываться по одному локальному адресу.

## 1. До выезда

На подготовочной машине:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/check_stack.sh
python3 ops/prod_readiness_audit.py
python3 ops/full_contour_audit.py
python3 ops/audit_onlyoffice_integration.py
bash ops/create_portable_bundle.sh --with-local-ldap
```

Проверить, что bundle реально собран:

1. есть каталог `runtime/portable-bundles/...`
2. внутри есть `install_everything.sh`
3. внутри есть `START_HERE.txt`
4. внутри есть `artifacts/docker-images.tar`
5. внутри есть `config/.env`

## 2. Что спросить у местного администратора

Нужно только это:

1. какой статический IP будет у сервера
2. открыт ли доступ к серверу по `443/tcp` из локальной сети
3. есть ли `docker` и `docker compose`, или их надо поставить
4. хватит ли ресурсов сервера под same-host live office слой

Если планируется live `DocSpace + Workspace` на том же сервере, ориентир по минимуму:

1. `6+ CPU`
2. `20 GiB RAM`
3. `12 GiB swap`
4. `80 GiB` свободного диска только под office-layer и его данные

Если этого нет, первая выкладка должна идти в `shell_only`, без финального live office cutover.

## 3. Безопасный первый запуск

На сервере:

```bash
cd /path/to/bundle
bash install_everything.sh /opt/docflow
```

Это безопасный базовый сценарий для первой выкладки в закрытой сети.

Он:

1. ставит основной контур
2. поднимает `Rukovoditel`, `Bridge`, `NauDoc`, `ONLYOFFICE Docs`
3. включает `DocSpace/Workspace` в рабочем frontdoor-режиме
4. выводит адреса входа по локальному IP

## 4. Когда можно включать live DocSpace и Workspace

Включать same-host live office слой только если одновременно:

1. `python3 ops/office_wave1_host_audit.py` на целевом сервере не ругается на `combined_same_host`
2. есть `root` или `sudo`
3. основной контур уже поднялся и прошел `check_stack`

Тогда cutover:

```bash
cd /opt/docflow
sudo bash ops/install_office_live_same_host.sh --auto-host
```

Если нужен one-shot путь сразу при установке:

```bash
cd /path/to/bundle
sudo bash install_everything.sh --with-live-office --office-auto-host /opt/docflow
```

## 5. Что проверить сразу после установки

На сервере:

```bash
cd /opt/docflow
bash ops/check_stack.sh
bash ops/smoke_test_stack.sh
python3 ops/monitoring_snapshot.py
python3 ops/prod_readiness_audit.py
```

Если делали live office cutover, дополнительно:

```bash
cd /opt/docflow
python3 ops/office_wave1_host_audit.py
python3 ops/audit_ecosystem_integration.py
python3 ops/audit_onlyoffice_integration.py
python3 ops/full_contour_audit.py
```

## 6. Что дать пользователям

Если DNS в больнице не готов, пользователям дается один локальный адрес по IP:

1. `https://<server-ip>/`

Внутри него уже доступны:

1. `https://<server-ip>/` — основной контур
2. `https://<server-ip>/docs/` — официальный контур `NauDoc`
3. `https://<server-ip>/office/` — `ONLYOFFICE Docs`
4. `https://<server-ip>/docspace/` — `DocSpace`
5. `https://<server-ip>/workspace/` — `Workspace`

Готовая памятка с адресами сохраняется в:

```bash
cat /opt/docflow/runtime/monitoring/access_points.txt
```

## 7. Что прокликать руками

Минимум:

1. `admin` входит на главную
2. `doctor` открывает Word-документ, правит и сохраняет
3. `nurse` открывает Excel-таблицу, правит и сохраняет
4. `head` открывает `Создать встречу`
5. `office` видит служебный документ и официальный контур
6. `DocSpace` и `Workspace` открываются без редиректов на чужие адреса

## 8. Когда считаем сервер готовым к пилоту

Сервер готов, если одновременно:

1. `check_stack` зеленый
2. `prod_readiness_audit.py` дает `0 blockers`
3. Word и Excel сохраняются в существующий файл
4. пользователи заходят по локальному адресу
5. `DocSpace/Workspace` открываются корректно хотя бы в frontdoor-режиме

## 9. Что делать, если live office слой не взлетел

Не блокировать весь запуск.

Нормальный fallback первой волны:

1. оставить основной контур поднятым
2. вернуть `DocSpace/Workspace` в `shell_only`
3. дать пользователям основной адрес
4. продолжить пилот на `Rukovoditel + ONLYOFFICE Docs + NauDoc`

Для возврата:

```bash
cd /opt/docflow
bash ops/configure_office_wave1.sh --docspace-shell-only --workspace-shell-only
bash ops/check_stack.sh
python3 ops/prod_readiness_audit.py
```

## 10. Честный критерий прод-готовности

Repo-side считаем готовым, когда:

1. bundle собран
2. install scripts и cutover scripts проходят локальные проверки
3. основное ядро проходит full verification

Инфраструктурно считаем готовым, когда:

1. сервер выдерживает нагрузку
2. локальный адрес доступен пользователям
3. роли и пользователи подтверждены
4. выбран хотя бы один пилотный маршрут документов

