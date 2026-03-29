# Bootstrap Seed

Этот каталог нужен для git-bootstrap установки без отдельного portable bundle.

Содержимое:

1. `mariadb/rukovoditel.sql` — baseline дамп рабочей БД
2. `bridge/bridge.db` — baseline база связей Bridge
3. `uploads/rukovoditel_uploads.tar.gz` — baseline uploads для карточек и файлов

`NauDoc Data.fs` здесь не дублируется.
Для git-bootstrap сценария берется уже отслеживаемый файл:

- [Data.fs](/home/lebedeffson/Code/Документооборот/naudoc_project/var/Data.fs)

Назначение:

1. дать локальному администратору сценарий "клонировали репозиторий и запустили install_from_git.sh"
2. не зависеть от отдельного backup-каталога рядом
3. не хранить здесь отдельные runtime-секреты

Важно:

1. это baseline под стартовую hospital-like выкладку и локальный пилот
2. если нужен offline-сценарий без интернета, использовать надо portable bundle, а не git bootstrap
