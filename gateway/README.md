# Gateway

Единый внешний вход для тестового production-lite контура.

## Что дает

1. один внешний HTTP-вход: `http://localhost:18090`
2. один внешний HTTPS-вход: `https://localhost:18443`
3. маршрутизацию:
   - `/` -> `Rukovoditel`
   - `/docs/` -> `NauDoc`
   - `/bridge/` -> `middleware`
   - `/docspace/` -> `ONLYOFFICE DocSpace` frontdoor
   - `/workspace/` -> `ONLYOFFICE Workspace` frontdoor

## Запуск

```bash
cd /home/lebedeffson/Code/Документооборот/gateway
docker compose up -d --build
```

## Проверка

```bash
curl -I http://localhost:18090
curl -k https://localhost:18443/healthz
curl -k https://localhost:18443/bridge/health
curl -k -I https://localhost:18443/docspace/
curl -k -I https://localhost:18443/workspace/
```

## Примечания

1. для локального стенда используется self-signed сертификат
2. сертификат создается автоматически при первом старте
3. в реальном production его нужно заменить на нормальный сертификат
4. если `DOCSPACE_TARGET_URL/WORKSPACE_TARGET_URL` пусты, `/docspace/` и `/workspace/` работают как shell-страницы первой волны
5. если target URL задан, frontdoor работает как live gateway entrypoint:
   - для same-host схемы проксирует сервис под тем же адресом `/docspace/` или `/workspace/`
   - для отдельных office-hosts может использоваться как target-aware frontdoor
6. shell остается доступен через `?shell=1` или `index.php?module=dashboard/ecosystem`
7. для закрытой локальной сети preferred-модель: один внешний адрес gateway и внутренние target URL вида `http://host.docker.internal:<port>/`
8. для офлайн-выезда можно оставить `DOCFLOW_ACCESS_HOST=` пустым и `DOCFLOW_ACCESS_HOST_AUTO=1`, тогда gateway и публичные URL автоматически переключатся на основной IP сервера при первом старте
