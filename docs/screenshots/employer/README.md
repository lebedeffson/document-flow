# Скриншоты для работодателя

Скриншоты собраны автоматически из живого стенда.

Набор:

- `01-login.png` — экран входа с разделением на режимы
- `02-admin-dashboard.png` — администраторская главная
- `03-admin-tasks.png` — администраторский раздел задач
- `04-admin-requests.png` — администраторский раздел заявок
- `05-admin-projects.png` — администраторский раздел проектов
- `06-admin-discussions.png` — администраторский раздел обсуждений
- `07-admin-documents.png` — администраторский раздел документов
- `08-admin-document-base.png` — администраторская база документов
- `09-admin-mts.png` — администраторский раздел МТЗ
- `10-admin-control-report.png` — контрольный отчет руководителя
- `11-user-dashboard.png` — пользовательская главная
- `12-user-requests.png` — пользовательский раздел заявок
- `13-user-tasks.png` — пользовательский раздел задач
- `14-user-projects.png` — пользовательский раздел проектов
- `15-user-documents.png` — пользовательский раздел документов
- `16-user-document-card.png` — карточка документа
- `17-user-document-base.png` — база документов
- `18-user-mts.png` — раздел МТЗ
- `19-onlyoffice-editor.png` — совместное редактирование в `ONLYOFFICE`
- `20-naudoc-home.png` — официальный документный контур `NauDoc`
- `21-naudoc-storage.png` — хранилище `NauDoc`
- `22-naudoc-staff-directory.png` — справочник сотрудников в `NauDoc`
- `23-bridge-overview.png` — интеграционный контур `Bridge`

Команда для пересборки:

```bash
cd /home/lebedeffson/Code/Документооборот
PLAYWRIGHT_BROWSER=chromium node ops/capture_employer_screenshots.mjs
```
