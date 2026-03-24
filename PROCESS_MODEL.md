# Process Model for Test Stand

This process model configures `Rukovoditel` for the joint `NauDoc + Middleware + Rukovoditel` stand.

## Entity groups

- `Операционная работа`
- `Документы`
- `Обеспечение`

## Main entities

- `Проекты и инициативы`
- `Поручения и задачи`
- `Заявки на обслуживание`
- `Карточки документов`
- `База документов`
- `Заявки на МТЗ`

## Principles

- `NauDoc` remains the source of truth for document files, approvals, archive, and legacy document routes.
- `Rukovoditel` becomes the operational workspace for projects, requests, tasks, and control work.
- Middleware stores the bridge between operational records and document cards/links.

## Immediate goal of this setup

- make the system understandable to end users
- separate operational work from document storage
- give managers and teachers a clearer top-level structure
- prepare a base for status synchronization later
