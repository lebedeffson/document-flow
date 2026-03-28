# Staging Runbook

`Staging` нужен как отдельный предрелизный контур перед выкладкой в больницу.

## Базовый принцип

1. staging не должен делить боевые порты с production
2. staging не должен использовать production `.env`
3. staging должен проходить тот же `verify`, что и production-candidate

## Как подготовить env

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/generate_staging_env.sh
```

По умолчанию получится:

1. `.env.generated.staging`
2. домен `staging.docflow.hospital.local`
3. отдельные bind-порты:
   - gateway `28090/28443`
   - `Rukovoditel` `28081`
   - `Bridge` `28082`
   - `NauDoc` `28080`
   - `ONLYOFFICE` `28083`

## Как запускать staging

Лучший вариант:

1. отдельный checkout или отдельная директория на сервере
2. отдельный `.env`
3. отдельные compose project names из staging env

Для подпроектов запускать с явным env:

```bash
docker compose --env-file /opt/docflow-staging/.env -f middleware/docker-compose.yml up -d --build
docker compose --env-file /opt/docflow-staging/.env -f rukovoditel-test/docker-compose.yml up -d --build
docker compose --env-file /opt/docflow-staging/.env -f gateway/docker-compose.yml up -d --build
docker compose --env-file /opt/docflow-staging/.env -f docker-compose.legacy.yml up -d --build
```

## Что обязательно проверить на staging

1. `python3 ops/prod_readiness_audit.py`
2. `bash ops/check_stack.sh`
3. `bash ops/smoke_test_stack.sh`
4. `bash ops/run_full_verification.sh`
5. `bash ops/restore_drill.sh`

## Release gate

В production пускаем только сборку, где:

1. `prod_readiness_audit` без blocker'ов
2. `run_full_verification` зеленый
3. `restore_drill` успешный
4. monitoring snapshot пишет `status=ok` или понятный `warning` без падения core-сервисов
