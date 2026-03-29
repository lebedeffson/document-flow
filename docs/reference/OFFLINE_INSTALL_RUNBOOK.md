# Offline Install Runbook

Цель: подготовить bundle на рабочей машине, перенести его на флешке и поднять платформу на Linux-сервере без обязательного доступа в интернет.

Короткий боевой сценарий именно под hospital LAN:

- [CLOSED_LAN_GO_LIVE_CHECKLIST.md](/home/lebedeffson/Code/Документооборот/docs/reference/CLOSED_LAN_GO_LIVE_CHECKLIST.md)

## 1. Что должно быть на сервере

Нужно только:

1. Linux-сервер
2. `docker`
3. `docker compose`
4. свободное место под:
   - контейнеры
   - образы
   - backup snapshot

Интернет для установки самого контура не требуется, если bundle уже собран полностью.

## 2. Как собрать bundle

На подготовленной машине:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/create_portable_bundle.sh --with-local-ldap
```

Скрипт соберет:

1. архив проекта
2. архив snapshot-данных
3. архив Docker-образов
4. копию `.env`
5. `install_from_bundle.sh`
6. `install_everything.sh`
7. `START_HERE.txt`

Если нужно сначала только проверить готовность:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/create_portable_bundle.sh --verify-only --with-local-ldap
```

## 3. Что перенести на флешку

Нужно перенести целиком каталог bundle, который создал `create_portable_bundle.sh`.

Внутри него будут:

1. `artifacts/project.tar.gz`
2. `artifacts/backup.tar.gz`
3. `artifacts/docker-images.tar`
4. `config/.env`
5. `install_from_bundle.sh`
6. `install_everything.sh`
7. `START_HERE.txt`

## 4. Как поставить на сервере

На сервере есть два варианта.

Самый простой, под сценарий "одна команда с флешки":

```bash
cd /path/to/bundle
bash install_everything.sh /opt/docflow
```

Этот сценарий:

1. проверяет bundle и зависимости
2. ставит проект
3. поднимает контейнеры
4. восстанавливает snapshot
5. прогоняет production readiness preflight по `.env` и останавливается, если есть blockers
6. включает `Office Wave 1` в готовом режиме
7. печатает адреса входа
8. прогоняет базовую post-install проверку

Низкоуровневый вариант, если нужен только базовый install:

```bash
cd /path/to/bundle
bash install_from_bundle.sh /opt/docflow
```

Что произойдет:

1. проект распакуется в `/opt/docflow`
2. `.env` установится в корень проекта
3. install-скрипт сразу проверит production readiness и не пойдет дальше, если `.env` остался небезопасным
4. Docker-образы загрузятся локально
5. контейнеры поднимутся без `build` и без `pull`
6. данные восстановятся из snapshot
7. после этого пройдет `check_stack.sh`

Если bundle собран с локальным LDAP baseline, он тоже поднимется и будет синхронизирован через `Bridge`.

## 4.1 Что теперь происходит с адресами автоматически

При первом запуске install-скрипт теперь:

1. определяет основной IPv4 сервера
2. переписывает все публичные URL в `.env` через этот адрес
3. печатает готовую памятку с адресами входа
4. сохраняет ее в `runtime/monitoring/access_points.txt`

То есть в незнакомой локальной сети можно стартовать даже без заранее известного DNS.

Если в bundle `.env` оставить:

```env
DOCFLOW_ACCESS_HOST=
DOCFLOW_ACCESS_HOST_AUTO=1
DOCSPACE_TARGET_URL=
WORKSPACE_TARGET_URL=
DOCFLOW_WORKSPACE_WAVE1_ENABLE_COMMUNITY=0
DOCSPACE_COLLABORATION_ROOM_TARGET_URL=
DOCSPACE_PUBLIC_ROOM_TARGET_URL=
DOCSPACE_FORM_FILLING_ROOM_TARGET_URL=
WORKSPACE_CALENDAR_TARGET_URL=
WORKSPACE_COMMUNITY_TARGET_URL=
```

то после установки платформа будет доступна по IP сервера, а сервисы первой волны будут открываться так:

1. `https://<server-ip>/` -> основная платформа
2. `https://<server-ip>/office/` -> `ONLYOFFICE Docs`
3. `https://<server-ip>/docspace/` -> `ONLYOFFICE DocSpace` frontdoor
4. `https://<server-ip>/workspace/` -> `ONLYOFFICE Workspace` frontdoor

Для первой волны `install_everything.sh` по умолчанию ставит lean-mode:

1. `DocSpace` доступен через встроенный frontdoor
2. `Workspace` доступен через встроенный frontdoor
3. `Calendar` доступен всем пользователям
4. `Community` по умолчанию выключен

Если позже на том же сервере поднимутся живые `DocSpace` и `Workspace`, их можно не выносить на отдельные внешние адреса. Для закрытой сети допустим same-host reverse proxy режим, и пользователи по-прежнему будут заходить только так:

1. `https://<server-ip>/`
2. `https://<server-ip>/docspace/`
3. `https://<server-ip>/workspace/`

Полный live office cutover описан ниже в разделе `4.2`.

Если позже появится локальный DNS alias, достаточно поменять только `.env`:

```env
DOCFLOW_ACCESS_HOST=docflow.hospital.local
DOCFLOW_ACCESS_HOST_AUTO=0
```

и затем перезапустить стек.

Важно: `hosts` на сервере влияет только на сам сервер. Чтобы все рабочие станции открывали alias, нужен либо локальный DNS, либо `hosts` на каждом клиентском ПК.


## 4.2 Как включить живые DocSpace и Workspace на том же сервере

Если на целевом сервере достаточно ресурсов и есть `sudo`, после базовой установки можно включить настоящий live office-layer на том же IP-адресе.

Сначала убедиться, что официальный installer-пакет лежит в проекте:

```bash
cd /opt/docflow
ls ops/vendor/onlyoffice-installers
```

Потом выполнить one-shot сценарий:

```bash
cd /opt/docflow
sudo bash ops/install_office_live_same_host.sh --auto-host
```

Если хочется пройти все одним верхнеуровневым installer'ом, а не отдельным office-скриптом:

```bash
sudo bash install_everything.sh --with-live-office --office-auto-host /opt/docflow
```

Что он делает:

1. использует официальные installer'ы `ONLYOFFICE DocSpace` и `ONLYOFFICE Workspace`
2. поднимает `DocSpace` на внутреннем порту `19001`
3. поднимает `Workspace` на внутреннем порту `19002`
4. подключает `DocSpace` к уже работающему `ONLYOFFICE Docs`
5. отключает в `Workspace` тяжелые модули первой волны через наш lean cutover
6. включает `live_target` через тот же gateway

После этого пользователи по-прежнему заходят только по одному адресу:

1. `https://<server-ip>/`
2. `https://<server-ip>/docspace/`
3. `https://<server-ip>/workspace/`

Если нужно оставить только `Calendar` в `Workspace`, это поведение уже по умолчанию.
Если нужен и `Community`, можно использовать:

```bash
sudo bash ops/install_office_live_same_host.sh --auto-host --workspace-with-community
```

Важно:

1. этот шаг требует `root`
2. same-host live office слой тяжелый по ресурсам
3. перед запуском лучше убедиться, что сервер действительно тянет `DocSpace + Workspace + основной контур`

## 5. Что проверить после установки

```bash
cd /opt/docflow
bash ops/check_stack.sh
bash ops/smoke_test_stack.sh
python3 ops/prod_readiness_audit.py
```

После `install_everything.sh` отдельный JSON-отчет readiness лежит здесь:

```bash
cd /opt/docflow
cat runtime/monitoring/install_prod_readiness.json
```

И сразу посмотреть сохраненную памятку с адресами:

```bash
cd /opt/docflow
cat runtime/monitoring/access_points.txt
```

При необходимости полный прогон:

```bash
cd /opt/docflow
bash ops/run_full_verification.sh
```

## 6. Что важно

1. bundle содержит `.env` и секреты, поэтому его нужно хранить как чувствительный носитель
2. backup snapshot теперь включает и `Rukovoditel uploads`, поэтому восстановление полноценное
3. для production с реальным hospital `LDAP/AD` локальный LDAP baseline можно не включать
