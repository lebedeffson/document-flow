#!/usr/bin/env bash
set -euo pipefail

DEFAULT_REPO_URL="https://github.com/lebedeffson/document-flow.git"
DEFAULT_BRANCH="main"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKOUT_DIR="/opt/document-flow"
REPO_URL="${DEFAULT_REPO_URL}"
BRANCH="${DEFAULT_BRANCH}"
INSTALL_PREREQS_MODE="auto"
WITH_LOCAL_LDAP=1
WITH_LIVE_OFFICE=0
OFFICE_AUTO_HOST=0
OFFICE_HOST=""
DOCSPACE_PORT=""
WORKSPACE_PORT=""
WORKSPACE_SCOPE="calendar_only"
SKIP_OFFICE_HARDWARE_CHECK=0
SIMPLE_PASSWORDS=0
VERIFY_ONLY=0
FORCE_CLONE=0
SKIP_UPDATE=0

usage() {
  cat <<'EOF'
Usage:
  bash install_server.sh [options]

Назначение:
  Один bootstrap-файл для Linux-сервера. Он сам:
  1. при необходимости ставит prerequisites
  2. берет или обновляет git checkout проекта
  3. запускает полноценную установку платформы

Options:
  --checkout-dir <path>        Where the project git checkout should live
  --repo-url <url-or-path>     Git repo URL or local path
  --branch <name>              Git branch to clone/pull
  --force-clone                Ignore current checkout and always clone/update target dir
  --skip-update                Do not pull an existing checkout
  --install-prereqs            Force prerequisite installation on apt/dnf/yum-based Linux
  --skip-prereqs               Skip prerequisite installation even when running as root
  --without-local-ldap         Skip local LDAP baseline
  --with-live-office           Install live DocSpace + Workspace after base install
  --office-host <dns-or-ip>    Public host/IP for live office cutover
  --office-auto-host           Auto-detect the primary IPv4 for live office cutover
  --docspace-port <port>       Internal DocSpace port for same-host live mode
  --workspace-port <port>      Internal Workspace port for same-host live mode
  --workspace-with-community   Keep Calendar and expose Community
  --workspace-calendar-only    Keep only Calendar in Workspace Wave 1
  --skip-office-hardware-check Skip host guard for live office
  --simple-passwords           Use admin2026 / test2026 for bootstrap users
  --verify-only                Clone/update and validate install prerequisites without installing
  -h, --help                   Show help

Examples:
  sudo bash install_server.sh
  sudo bash install_server.sh --simple-passwords
  sudo bash install_server.sh --with-live-office --office-auto-host
  bash install_server.sh --verify-only --force-clone --checkout-dir /tmp/document-flow
EOF
}

log() {
  echo "[install-server] $*" >&2
}

fail() {
  echo "[install-server] ERROR: $*" >&2
  exit 1
}

have_command() {
  command -v "${1:-}" >/dev/null 2>&1
}

ensure_git_for_clone() {
  if have_command git; then
    return 0
  fi

  [ "$(id -u)" -eq 0 ] || fail "git is missing; rerun with sudo or install git manually"
  export DEBIAN_FRONTEND=noninteractive

  if have_command apt-get; then
    log "install minimal clone prerequisites via apt"
    apt-get update
    apt-get install -y --no-install-recommends ca-certificates curl git
    return 0
  fi

  if have_command dnf; then
    log "install minimal clone prerequisites via dnf"
    dnf install -y ca-certificates curl git
    return 0
  fi

  if have_command yum; then
    log "install minimal clone prerequisites via yum"
    yum install -y ca-certificates curl git
    return 0
  fi

  fail "git is missing and automatic bootstrap currently supports apt/dnf/yum-based Linux only"
}

should_use_current_checkout() {
  if [ "${FORCE_CLONE}" = "1" ]; then
    return 1
  fi

  [ -d "${SCRIPT_DIR}/.git" ] && [ -f "${SCRIPT_DIR}/ops/install_from_git.sh" ]
}

install_prereqs_if_needed() {
  local checkout_dir="${1:-}"

  case "${INSTALL_PREREQS_MODE}" in
    skip)
      return 0
      ;;
    force)
      ;;
    auto)
      if [ "$(id -u)" -ne 0 ]; then
        return 0
      fi
      ;;
    *)
      fail "unknown INSTALL_PREREQS_MODE=${INSTALL_PREREQS_MODE}"
      ;;
  esac

  if [ ! -f "${checkout_dir}/ops/install_server_prereqs.sh" ]; then
    fail "install_server_prereqs.sh is missing in ${checkout_dir}"
  fi

  log "install server prerequisites"
  bash "${checkout_dir}/ops/install_server_prereqs.sh"
}

clone_or_update_checkout() {
  local checkout_dir="${1:-}"
  local repo_url="${2:-}"
  local branch="${3:-}"

  ensure_git_for_clone

  mkdir -p "$(dirname "${checkout_dir}")"

  if [ -d "${checkout_dir}/.git" ]; then
    if [ "${SKIP_UPDATE}" = "1" ]; then
      log "using existing checkout without update: ${checkout_dir}"
      printf '%s\n' "${checkout_dir}"
      return 0
    fi

    log "update checkout: ${checkout_dir}"
    git -C "${checkout_dir}" fetch origin "${branch}" --depth 1
    git -C "${checkout_dir}" checkout "${branch}"
    git -C "${checkout_dir}" pull --ff-only origin "${branch}"
    printf '%s\n' "${checkout_dir}"
    return 0
  fi

  if [ -e "${checkout_dir}" ] && [ ! -d "${checkout_dir}/.git" ]; then
    fail "target checkout dir exists and is not a git checkout: ${checkout_dir}"
  fi

  log "clone repo: ${repo_url} -> ${checkout_dir}"
  git clone --branch "${branch}" --depth 1 "${repo_url}" "${checkout_dir}"
  printf '%s\n' "${checkout_dir}"
}

write_summary() {
  local checkout_dir="${1:-}"
  mkdir -p "${checkout_dir}/runtime/monitoring"
  cat > "${checkout_dir}/runtime/monitoring/install_server_summary.txt" <<EOF
installed_at=$(date -Iseconds)
checkout_dir=${checkout_dir}
repo_url=${REPO_URL}
branch=${BRANCH}
with_local_ldap=${WITH_LOCAL_LDAP}
with_live_office=${WITH_LIVE_OFFICE}
workspace_scope=${WORKSPACE_SCOPE}
simple_passwords=${SIMPLE_PASSWORDS}
verify_only=${VERIFY_ONLY}
force_clone=${FORCE_CLONE}
skip_update=${SKIP_UPDATE}
EOF
  log "summary: ${checkout_dir}/runtime/monitoring/install_server_summary.txt"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --checkout-dir)
      CHECKOUT_DIR="${2:-}"
      shift 2
      ;;
    --repo-url)
      REPO_URL="${2:-}"
      shift 2
      ;;
    --branch)
      BRANCH="${2:-}"
      shift 2
      ;;
    --force-clone)
      FORCE_CLONE=1
      shift
      ;;
    --skip-update)
      SKIP_UPDATE=1
      shift
      ;;
    --install-prereqs)
      INSTALL_PREREQS_MODE="force"
      shift
      ;;
    --skip-prereqs)
      INSTALL_PREREQS_MODE="skip"
      shift
      ;;
    --without-local-ldap)
      WITH_LOCAL_LDAP=0
      shift
      ;;
    --with-live-office)
      WITH_LIVE_OFFICE=1
      shift
      ;;
    --office-host)
      OFFICE_HOST="${2:-}"
      shift 2
      ;;
    --office-auto-host)
      OFFICE_AUTO_HOST=1
      shift
      ;;
    --docspace-port)
      DOCSPACE_PORT="${2:-}"
      shift 2
      ;;
    --workspace-port)
      WORKSPACE_PORT="${2:-}"
      shift 2
      ;;
    --workspace-with-community)
      WORKSPACE_SCOPE="with_community"
      shift
      ;;
    --workspace-calendar-only)
      WORKSPACE_SCOPE="calendar_only"
      shift
      ;;
    --skip-office-hardware-check)
      SKIP_OFFICE_HARDWARE_CHECK=1
      shift
      ;;
    --simple-passwords)
      SIMPLE_PASSWORDS=1
      shift
      ;;
    --verify-only)
      VERIFY_ONLY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown option: $1"
      ;;
  esac
done

if [ "${WITH_LIVE_OFFICE}" = "1" ] && [ "$(id -u)" -ne 0 ]; then
  fail "--with-live-office requires sudo/root"
fi

if should_use_current_checkout; then
  CHECKOUT_DIR="${SCRIPT_DIR}"
  log "use current checkout: ${CHECKOUT_DIR}"
else
  CHECKOUT_DIR="$(clone_or_update_checkout "${CHECKOUT_DIR}" "${REPO_URL}" "${BRANCH}")"
fi

install_prereqs_if_needed "${CHECKOUT_DIR}"

[ -f "${CHECKOUT_DIR}/install_from_git.sh" ] || fail "install_from_git.sh is missing in ${CHECKOUT_DIR}"

INSTALL_ARGS=()
if [ "${WITH_LOCAL_LDAP}" != "1" ]; then
  INSTALL_ARGS+=(--without-local-ldap)
fi
if [ "${WITH_LIVE_OFFICE}" = "1" ]; then
  INSTALL_ARGS+=(--with-live-office)
fi
if [ -n "${OFFICE_HOST}" ]; then
  INSTALL_ARGS+=(--office-host "${OFFICE_HOST}")
elif [ "${OFFICE_AUTO_HOST}" = "1" ]; then
  INSTALL_ARGS+=(--office-auto-host)
fi
if [ -n "${DOCSPACE_PORT}" ]; then
  INSTALL_ARGS+=(--docspace-port "${DOCSPACE_PORT}")
fi
if [ -n "${WORKSPACE_PORT}" ]; then
  INSTALL_ARGS+=(--workspace-port "${WORKSPACE_PORT}")
fi
if [ "${WORKSPACE_SCOPE}" = "with_community" ]; then
  INSTALL_ARGS+=(--workspace-with-community)
else
  INSTALL_ARGS+=(--workspace-calendar-only)
fi
if [ "${SKIP_OFFICE_HARDWARE_CHECK}" = "1" ]; then
  INSTALL_ARGS+=(--skip-office-hardware-check)
fi
if [ "${SIMPLE_PASSWORDS}" = "1" ]; then
  INSTALL_ARGS+=(--simple-passwords)
fi
if [ "${VERIFY_ONLY}" = "1" ]; then
  INSTALL_ARGS+=(--verify-only)
fi

log "delegate install: ${CHECKOUT_DIR}/install_from_git.sh"
(
  cd "${CHECKOUT_DIR}"
  bash install_from_git.sh "${INSTALL_ARGS[@]}"
)

write_summary "${CHECKOUT_DIR}"

if [ -f "${CHECKOUT_DIR}/ops/export_server_quickstart.sh" ]; then
  bash "${CHECKOUT_DIR}/ops/export_server_quickstart.sh" >/dev/null || true
fi

log "completed"
log "checkout: ${CHECKOUT_DIR}"
if [ -f "${CHECKOUT_DIR}/runtime/monitoring/START_HERE.txt" ]; then
  log "quick start: ${CHECKOUT_DIR}/runtime/monitoring/START_HERE.txt"
  cat "${CHECKOUT_DIR}/runtime/monitoring/START_HERE.txt"
fi
