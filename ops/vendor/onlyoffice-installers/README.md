# ONLYOFFICE Installer Cache

В этом каталоге лежат официальные installer-скрипты `ONLYOFFICE DocSpace` и `ONLYOFFICE Workspace`, которые используются нашими wrapper'ами для same-host установки в закрытой локальной сети.

Файлы скачиваются командой:

```bash
cd /home/lebedeffson/Code/Документооборот
bash ops/download_onlyoffice_installers.sh
```

Основные wrapper'ы:

```bash
sudo bash ops/install_docspace_same_host.sh --host <server-ip-or-dns>
sudo bash ops/install_workspace_same_host.sh
sudo bash ops/install_office_live_same_host.sh --auto-host
```

Что важно:

1. эти скрипты не заменяют `root`-права на целевом сервере
2. `DocSpace` и `Workspace` остаются тяжелыми сервисами, поэтому перед live-установкой нужно проверить ресурсы хоста
3. после установки финальный cutover выполняется через `ops/cutover_closed_lan_prod.sh`
