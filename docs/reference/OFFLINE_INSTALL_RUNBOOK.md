# Offline Install Runbook

Цель: подготовить bundle на рабочей машине, перенести его на флешке и поднять платформу на Linux-сервере без обязательного доступа в интернет.

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
5. install-скрипт для сервера

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

## 4. Как поставить на сервере

На сервере:

```bash
cd /path/to/bundle
bash install_from_bundle.sh /opt/docflow
```

Что произойдет:

1. проект распакуется в `/opt/docflow`
2. `.env` установится в корень проекта
3. Docker-образы загрузятся локально
4. контейнеры поднимутся без `build` и без `pull`
5. данные восстановятся из snapshot
6. после этого пройдет `check_stack.sh`

Если bundle собран с локальным LDAP baseline, он тоже поднимется и будет синхронизирован через `Bridge`.

## 5. Что проверить после установки

```bash
cd /opt/docflow
bash ops/check_stack.sh
bash ops/smoke_test_stack.sh
python3 ops/prod_readiness_audit.py
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
