# Git Install Runbook

Цель: дать сценарий, при котором локальный администратор больницы может скачать один bootstrap-файл, а дальше установка пройдет одной командой без участия разработчика.

Важно:

1. этот сценарий требует доступа сервера в интернет к GitHub и Docker Registry
2. если интернета на сервере нет, использовать нужно portable bundle, а не git bootstrap

## 1. Самый короткий путь

Если сервер видит GitHub и Docker Registry, достаточно:

```bash
curl -fsSL https://raw.githubusercontent.com/lebedeffson/document-flow/main/install_server.sh -o install_server.sh
sudo bash install_server.sh
```

Этот bootstrap:

1. при необходимости ставит prerequisites на apt/dnf/yum-based Linux
2. клонирует или обновляет git checkout
3. запускает `install_from_git.sh`
4. восстанавливает встроенный baseline
5. выводит адреса входа и summary

Для локального теста с простыми паролями:

```bash
sudo bash install_server.sh --simple-passwords
```

Для live office слоя:

```bash
sudo bash install_server.sh --with-live-office --office-auto-host
```

## 2. Что должно быть на сервере

Минимум:

1. Linux
2. `git`
3. `docker`
4. `docker compose`
5. доступ в интернет для скачивания образов и зависимостей

Если этого нет, можно попытаться поставить prerequisites одной командой:

```bash
sudo bash ops/install_server_prereqs.sh
```

## 3. Быстрый запуск из уже клонированного репозитория

Клонировать репозиторий:

```bash
git clone https://github.com/lebedeffson/document-flow.git
cd document-flow
```

Потом запустить:

```bash
bash install_from_git.sh
```

Или сначала проверить готовность checkout без изменения системы:

```bash
bash install_from_git.sh --verify-only
```

Что делает скрипт:

1. генерирует новый `.env`, если его еще нет
2. поднимает основной стек
3. восстанавливает встроенный baseline snapshot из репозитория
4. перепривязывает пользователей и baseline под текущий `.env`
5. печатает локальные адреса и создает LAN packet
6. прогоняет базовые проверки

## 4. Если нужны простые стартовые пароли

```bash
bash install_from_git.sh --simple-passwords
```

Тогда будет:

1. `admin / admin2026`
2. `head / test2026`
3. `doctor / test2026`
4. `nurse / test2026`
5. `registry / test2026`
6. `office / test2026`

Это допустимо только для первичного локального теста. Потом пароли нужно ротировать.

## 5. Если нужен local LDAP baseline

По умолчанию он уже включен.

Если не нужен:

```bash
bash install_from_git.sh --without-local-ldap
```

## 6. Если нужен live DocSpace + Workspace

Только на достаточно мощном сервере и только под `sudo`:

```bash
sudo bash install_from_git.sh --with-live-office --office-auto-host
```

Перед этим стоит проверить:

```bash
python3 ops/office_wave1_host_audit.py
```

## 7. Что смотреть после установки

1. `runtime/monitoring/access_points.txt`
2. `.tmp_lan_manual_test/LAN_MANUAL_TEST_PACKET.md`
3. `runtime/monitoring/git_install_summary.txt`

## 8. Когда этот сценарий не подходит

Не подходит, если:

1. на сервере нет интернета
2. нельзя поставить Docker
3. нет прав `sudo/root`, а нужны prerequisites или live office layer

В этом случае нужен portable bundle сценарий из:

- [OFFLINE_INSTALL_RUNBOOK.md](/home/lebedeffson/Code/Документооборот/docs/reference/OFFLINE_INSTALL_RUNBOOK.md)
