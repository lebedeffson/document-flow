#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUT_DIR="${ROOT_DIR}/ops/vendor/onlyoffice-installers"
REFRESH=0

usage() {
  cat <<'EOF'
Usage:
  bash ops/download_onlyoffice_installers.sh [options] [out-dir]

Options:
  --refresh     Re-download cached official installer scripts
  -h, --help    Show help
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --refresh)
      REFRESH=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [ "${OUT_DIR}" != "${ROOT_DIR}/ops/vendor/onlyoffice-installers" ]; then
        echo "Usage: $0 [--refresh] [out-dir]" >&2
        exit 1
      fi
      OUT_DIR="$1"
      shift
      ;;
  esac
done

REQUIRED_FILES=(
  "docspace/docspace-install.sh"
  "docspace/install-Docker.sh"
  "docspace/install-Docker-args.sh"
  "workspace/workspace-install.sh"
  "workspace/install.sh"
)

have_cached_installers() {
  local rel_path
  for rel_path in "${REQUIRED_FILES[@]}"; do
    if [ ! -s "${OUT_DIR}/${rel_path}" ]; then
      return 1
    fi
  done
  return 0
}

download_file() {
  local url="${1}"
  local path="${2}"
  mkdir -p "$(dirname "${path}")"
  curl -fL --retry 3 --retry-delay 2 -o "${path}" "${url}"
  chmod +x "${path}"
}

mkdir -p "${OUT_DIR}/docspace" "${OUT_DIR}/workspace"

if [ "${REFRESH}" != "1" ] && have_cached_installers; then
  echo "[onlyoffice-installers] using cached installers: ${OUT_DIR}"
else
  download_file "https://download.onlyoffice.com/docspace/docspace-install.sh" \
    "${OUT_DIR}/docspace/docspace-install.sh"
  download_file "https://download.onlyoffice.com/docspace/install-Docker.sh" \
    "${OUT_DIR}/docspace/install-Docker.sh"
  download_file "https://download.onlyoffice.com/docspace/install-Docker-args.sh" \
    "${OUT_DIR}/docspace/install-Docker-args.sh"

  download_file "https://download.onlyoffice.com/install/workspace-install.sh" \
    "${OUT_DIR}/workspace/workspace-install.sh"
  download_file "http://download.onlyoffice.com/install/install.sh" \
    "${OUT_DIR}/workspace/install.sh"
fi

cat > "${OUT_DIR}/MANIFEST.txt" <<EOF
downloaded_at=$(date -Iseconds)
refresh=${REFRESH}
docspace:
  docspace-install.sh <- https://download.onlyoffice.com/docspace/docspace-install.sh
  install-Docker.sh <- https://download.onlyoffice.com/docspace/install-Docker.sh
  install-Docker-args.sh <- https://download.onlyoffice.com/docspace/install-Docker-args.sh
workspace:
  workspace-install.sh <- https://download.onlyoffice.com/install/workspace-install.sh
  install.sh <- http://download.onlyoffice.com/install/install.sh
EOF

echo "[onlyoffice-installers] ready: ${OUT_DIR}"
