#!/usr/bin/env bash
set -euo pipefail

ES_CONTAINER="onlyoffice-elasticsearch"
COMMUNITY_CONTAINER="onlyoffice-community-server"
WAIT_SECONDS=30

usage() {
  cat <<'EOF'
Usage:
  bash ops/disable_workspace_search_same_host.sh [options]

Options:
  --es-container <name>         Elasticsearch container name
  --community-container <name>  Workspace community-server container name
  --wait-seconds <sec>          Wait timeout after restart/stop (default: 30)
  -h, --help                    Show help
EOF
}

fail() {
  echo "[workspace-low-memory] ERROR: $*" >&2
  exit 1
}

find_container() {
  local preferred="${1:-}"
  if [ -n "${preferred}" ] && docker inspect "${preferred}" >/dev/null 2>&1; then
    printf '%s\n' "${preferred}"
    return 0
  fi

  docker ps -a --format '{{.Names}}' | rg "(^|-)${preferred}(-[0-9]+)?$" | head -n 1 || true
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --es-container)
      ES_CONTAINER="${2:-}"
      shift 2
      ;;
    --community-container)
      COMMUNITY_CONTAINER="${2:-}"
      shift 2
      ;;
    --wait-seconds)
      WAIT_SECONDS="${2:-}"
      shift 2
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

[[ "${WAIT_SECONDS}" =~ ^[0-9]+$ ]] || fail "invalid wait timeout: ${WAIT_SECONDS}"

ES_CONTAINER="$(find_container "${ES_CONTAINER}")"
COMMUNITY_CONTAINER="$(find_container "${COMMUNITY_CONTAINER}")"

[ -n "${COMMUNITY_CONTAINER}" ] || fail "could not find Workspace community server container"

if [ -n "${ES_CONTAINER}" ]; then
  echo "[workspace-low-memory] disable Elasticsearch restart policy: ${ES_CONTAINER}"
  docker update --restart=no "${ES_CONTAINER}" >/dev/null
  if docker inspect "${ES_CONTAINER}" --format '{{.State.Running}}' 2>/dev/null | rg -qx 'true'; then
    echo "[workspace-low-memory] stop Elasticsearch: ${ES_CONTAINER}"
    docker stop "${ES_CONTAINER}" >/dev/null
  fi
else
  echo "[workspace-low-memory] Elasticsearch container not found; continuing"
fi

echo "[workspace-low-memory] restart Workspace community server"
docker restart "${COMMUNITY_CONTAINER}" >/dev/null

echo "[workspace-low-memory] wait for community server"
for _ in $(seq 1 "${WAIT_SECONDS}"); do
  if docker inspect "${COMMUNITY_CONTAINER}" --format '{{.State.Running}}' 2>/dev/null | rg -qx 'true'; then
    if [ -n "${ES_CONTAINER}" ]; then
      es_running="$(docker inspect "${ES_CONTAINER}" --format '{{.State.Running}}' 2>/dev/null || true)"
      if [ "${es_running}" = "false" ] || [ -z "${es_running}" ]; then
        echo "[workspace-low-memory] Workspace is running with search disabled"
        exit 0
      fi
    else
      echo "[workspace-low-memory] Workspace is running"
      exit 0
    fi
  fi
  sleep 1
done

docker ps --format 'table {{.Names}}\t{{.Status}}' | rg 'onlyoffice-(community-server|elasticsearch)' || true
fail "Workspace community server did not stabilize in ${WAIT_SECONDS}s"
