# Требования к серверу и установка для больницы

Дата актуальности: `2026-04-01`

Этот документ нужен местному администратору больницы.
Цель простая: подготовить один Linux-сервер, запустить одну команду и получить рабочую систему с понятными адресами и логинами.

## 1. Какая система нужна

Подходит:

1. `Ubuntu Server 24.04 LTS`
2. `Ubuntu Server 22.04 LTS`
3. обычная `Ubuntu 24.04 LTS`
4. обычная `Ubuntu 22.04 LTS`

Важно:

1. нужна именно `x86_64`
2. сервер должен быть отдельной машиной под систему, а не пользовательским рабочим ПК
3. если выбирать из двух вариантов, предпочтительнее `Ubuntu Server`, но обычная `Ubuntu` тоже допустима

## 2. Какой сервер нужен

### Рекомендуемый стартовый профиль для больницы

Для первого запуска, теста и пилота:

1. `8 vCPU`
2. `16 GB RAM`
3. `8 GB swap`
4. `SSD/NVMe 240 GB+`
5. `1 статический IP`

Этот профиль допускается для low-load production первого этапа.

Что это значит:

1. основной контур работает полностью
2. `DocSpace` работает
3. `Workspace` работает
4. в `Workspace` временно отключается полнотекстовый поиск
5. `Calendar` и базовый портал `Workspace` остаются рабочими

Если после пилота системе добавят память, можно перейти к более комфортному full-capacity режиму.

### Желательно для более спокойного production

1. `8-12 vCPU`
2. `32 GB RAM`
3. `12-16 GB swap`
4. `SSD/NVMe 500 GB`

## 3. Как разделить диск

Самый практичный вариант:

1. `EFI` — `512 MB`
2. `/boot` — `1 GB`
3. `/` — `80 GB`
4. `/var/lib/docker` — все остальное
5. `swapfile` — `8 GB`

Если администратор не хочет отдельную разметку, допустим и упрощенный вариант:

1. один большой `/`
2. отдельный `swapfile 8 GB`

Но лучше все же вынести `/var/lib/docker` отдельно, потому что именно там будут лежать контейнеры и данные.

### Если у сервера два диска: `SSD` под систему и `HDD` под данные

Это допустимый и нормальный вариант.

Рекомендуемая схема:

1. `Ubuntu` ставится на `SSD`
2. второй диск монтируется, например, в `/srv/docflow-data`
3. установка запускается с ключом `--data-root /srv/docflow-data`

Важно:

1. `RAID` для схемы `SSD + HDD` не обязателен
2. второй диск нужно именно примонтировать до запуска установки
3. если второй диск не примонтирован, ключ `--data-root` указывать не нужно

Технически это означает следующее:

1. второй диск должен быть отформатирован и примонтирован как отдельная файловая система
2. точка монтирования может быть, например, `/srv/docflow-data`
3. монтирование должно быть постоянным и переживать перезагрузку сервера
4. на практике администратор обычно делает это через `UUID` в `/etc/fstab`, но для нас важен именно результат: путь `/srv/docflow-data` должен уже существовать и быть реальной точкой монтирования второго диска до запуска установки

## 4. Что должно быть подготовлено заранее

Нужно только это:

1. статический IP сервера
2. доступ к серверу по `443/tcp` из локальной сети больницы
3. `sudo/root`
4. корректное время и timezone на сервере

Если установка будет из git:

1. сервер должен видеть `GitHub`
2. сервер должен видеть `Docker Registry`
3. `Docker`, `docker compose` и `git` заранее ставить не обязательно: bootstrap-установщик поставит их сам
4. если данные должны лежать на втором диске, этот диск должен быть уже примонтирован до запуска установки

Если интернета не будет:

1. установка делается с portable bundle с флешки
2. интернет серверу тогда не нужен

## 5. Как ставится система

### Вариант A. Сервер видит интернет

Самый простой путь:

```bash
curl -fsSL https://raw.githubusercontent.com/lebedeffson/document-flow/main/install_server.sh -o install_server.sh
sudo bash install_server.sh --with-live-office --office-auto-host --simple-passwords
```

Если на сервере только чистая `Ubuntu` и даже `curl` еще не установлен:

```bash
sudo apt update
sudo apt install -y curl
curl -fsSL https://raw.githubusercontent.com/lebedeffson/document-flow/main/install_server.sh -o install_server.sh
sudo bash install_server.sh --with-live-office --office-auto-host --simple-passwords
```

Если систему нужно оставить на `SSD`, а persistent-данные держать на втором диске, запуск такой:

```bash
curl -fsSL https://raw.githubusercontent.com/lebedeffson/document-flow/main/install_server.sh -o install_server.sh
sudo bash install_server.sh --with-live-office --office-auto-host --simple-passwords --data-root /srv/docflow-data
```

Что делает эта команда:

1. ставит зависимости при необходимости
2. если нужно, ставит `git`, `docker`, `docker compose`, `python3`, `tar`
3. скачивает проект
4. поднимает основной контур
5. поднимает `DocSpace`
6. поднимает `Workspace`
7. на сервере с `16 GB` автоматически включает low-memory режим
8. если указан `--data-root`, выносит persistent container data на этот путь
9. создает текстовый файл с адресами и логинами

### Вариант B. Сервер в закрытой сети

Если интернета на сервере нет, используется portable bundle с флешки:

```bash
sudo bash install_everything.sh --with-live-office --office-auto-host /opt/docflow
```

Если данные нужно хранить на примонтированном втором диске:

```bash
sudo bash install_everything.sh --with-live-office --office-auto-host --data-root /srv/docflow-data /opt/docflow
```

## 6. Что появится после установки

На сервере будет создан простой текстовый файл.

Если установка из git по умолчанию:

```bash
/opt/document-flow/runtime/monitoring/START_HERE.txt
```

Если установка из portable bundle:

```bash
/opt/docflow/runtime/monitoring/START_HERE.txt
```

Именно его нужно открыть первым:

```bash
cat /opt/document-flow/runtime/monitoring/START_HERE.txt
```

В нем уже будут:

1. основной адрес системы
2. IP сервера
3. адреса `NauDoc`, `Bridge`, `ONLYOFFICE`, `DocSpace`, `Workspace`
4. логины и пароли
5. что проверить первым делом

## 7. Какие адреса получит больница

Если локальный DNS еще не готов, пользователи смогут заходить по IP:

1. `https://<server-ip>/` — основная платформа
2. `https://<server-ip>/docs/` — `NauDoc`
3. `https://<server-ip>/bridge/` — `Bridge`
4. `https://<server-ip>/office/` — `ONLYOFFICE Docs`
5. `https://<server-ip>/docspace/` — `DocSpace`
6. `https://<server-ip>/workspace/` — `Workspace`

## 8. Какие логины можно дать для первого теста

Если установка запускалась с `--simple-passwords`, стартовый набор такой:

1. `admin / admin2026`
2. `head / test2026`
3. `doctor / test2026`
4. `nurse / test2026`
5. `registry / test2026`
6. `office / test2026`

Это допустимо только для первичного локального теста и пилота.
Перед постоянной эксплуатацией пароли нужно заменить.

## 9. Что проверить после установки

Минимум:

1. открыть главную страницу платформы
2. войти под `doctor`
3. открыть Word-документ и сохранить изменения
4. войти под `head` или `nurse`
5. открыть Excel-таблицу и сохранить изменения
6. открыть `DocSpace`
7. открыть `Workspace Calendar`

## 10. Что важно понимать честно

При `16 GB RAM` система готова для первого реального запуска и оценки в больнице, если:

1. пользователей немного
2. документов немного
3. нагрузка небольшая
4. это первый этап до увеличения памяти

В таком профиле основная платформа уже работает как production-система.
Компромисс только один: `Workspace` временно работает без полнотекстового поиска.

## 11. Основные документы проекта

1. [PROJECT_SYSTEM_PASSPORT.md](/home/lebedeffson/Code/Документооборот/docs/reference/PROJECT_SYSTEM_PASSPORT.md)
2. [CLOSED_LAN_GO_LIVE_CHECKLIST.md](/home/lebedeffson/Code/Документооборот/docs/reference/CLOSED_LAN_GO_LIVE_CHECKLIST.md)
3. [GIT_INSTALL_RUNBOOK.md](/home/lebedeffson/Code/Документооборот/docs/reference/GIT_INSTALL_RUNBOOK.md)
