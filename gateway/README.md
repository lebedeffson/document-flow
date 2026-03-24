# Gateway

Единый внешний вход для тестового production-lite контура.

## Что дает

1. один внешний HTTP-вход: `http://localhost:18090`
2. один внешний HTTPS-вход: `https://localhost:18443`
3. маршрутизацию:
   - `/` -> `Rukovoditel`
   - `/docs/` -> `NauDoc`
   - `/bridge/` -> `middleware`

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
```

## Примечания

1. для локального стенда используется self-signed сертификат
2. сертификат создается автоматически при первом старте
3. в реальном production его нужно заменить на нормальный сертификат
