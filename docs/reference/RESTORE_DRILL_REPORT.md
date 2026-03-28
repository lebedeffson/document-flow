# Restore Drill Report

Дата: `2026-03-28T22:31:50+03:00`

## Результат

1. Backup создан: `/home/lebedeffson/Code/Документооборот/backups/restore-drill-20260328-223127`
2. Верификация backup: `ok`
3. Restore из свежего backup: `ok`
4. Post-restore stack check: `ok`
5. Post-restore smoke test: `ok`

## Артефакты

1. Backup: `/home/lebedeffson/Code/Документооборот/backups/restore-drill-20260328-223127`
2. Stack log: `/tmp/docflow-restore-drill-check.log`
3. Smoke log: `/tmp/docflow-restore-drill-smoke.log`

## Комментарий

Проверка выполнена на локальном связанном контуре.  
Для hospital production следующий шаг — повторить тот же drill на staging-контуре перед первым релизом.
