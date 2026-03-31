#!/usr/bin/env bash
set -euo pipefail

ES_CONTAINER="onlyoffice-elasticsearch"
COMMUNITY_CONTAINER="onlyoffice-community-server"
LOW_MEMORY_PROFILE=0
HEAP_MB=""
WAIT_SECONDS=60

usage() {
  cat <<'EOF'
Usage:
  bash ops/tune_workspace_same_host.sh [options]

Options:
  --es-container <name>         Elasticsearch container name
  --community-container <name>  Workspace community-server container name
  --low-memory-profile          Recreate Elasticsearch with a smaller heap for ~16 GB hosts
  --heap-mb <mb>                Explicit Elasticsearch heap size in MB
  --wait-seconds <sec>          Wait timeout after recreation (default: 60)
  -h, --help                    Show help
EOF
}

fail() {
  echo "[workspace-tune] ERROR: $*" >&2
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
    --low-memory-profile)
      LOW_MEMORY_PROFILE=1
      shift
      ;;
    --heap-mb)
      HEAP_MB="${2:-}"
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
if [ -n "${HEAP_MB}" ]; then
  [[ "${HEAP_MB}" =~ ^[0-9]+$ ]] || fail "invalid heap size: ${HEAP_MB}"
fi

ES_CONTAINER="$(find_container "${ES_CONTAINER}")"
[ -n "${ES_CONTAINER}" ] || fail "could not find Elasticsearch container"
COMMUNITY_CONTAINER="$(find_container "${COMMUNITY_CONTAINER}")"

NETWORK="$(
  docker inspect "${ES_CONTAINER}" --format '{{range $k, $v := .NetworkSettings.Networks}}{{println $k}}{{end}}' | head -n 1
)"
IMAGE="$(docker inspect "${ES_CONTAINER}" --format '{{.Config.Image}}')"
DATA_MOUNT="$(
  docker inspect "${ES_CONTAINER}" --format '{{range .Mounts}}{{if eq .Destination "/usr/share/elasticsearch/data"}}{{if eq .Type "volume"}}{{.Name}}:/usr/share/elasticsearch/data{{else}}{{.Source}}:/usr/share/elasticsearch/data{{end}}{{end}}{{end}}'
)"
CURRENT_OPTS="$(
  docker inspect "${ES_CONTAINER}" --format '{{range .Config.Env}}{{println .}}{{end}}' \
    | awk -F= '/^ES_JAVA_OPTS=/{sub(/^ES_JAVA_OPTS=/,""); print; exit}'
)"

[ -n "${NETWORK}" ] || fail "could not detect Elasticsearch network"
[ -n "${IMAGE}" ] || fail "could not detect Elasticsearch image"
[ -n "${DATA_MOUNT}" ] || fail "could not detect Elasticsearch data mount"

if [ -z "${HEAP_MB}" ]; then
  if [ "${LOW_MEMORY_PROFILE}" = "1" ]; then
    HEAP_MB="384"
  else
    HEAP_MB="$(printf '%s\n' "${CURRENT_OPTS}" | sed -n 's/.*-Xms\([0-9][0-9]*\)m.*/\1/p' | head -n 1)"
    [ -n "${HEAP_MB}" ] || HEAP_MB="512"
  fi
fi

FIELD_CACHE_SIZE="30%"
INDEX_BUFFER_SIZE="30%"
if [ "${LOW_MEMORY_PROFILE}" = "1" ]; then
  FIELD_CACHE_SIZE="20%"
  INDEX_BUFFER_SIZE="20%"
fi

echo "[workspace-tune] recreate ${ES_CONTAINER}"
echo "[workspace-tune] network=${NETWORK}"
echo "[workspace-tune] heap_mb=${HEAP_MB}"
docker rm -f "${ES_CONTAINER}" >/dev/null 2>&1 || true

docker run \
  --name "${ES_CONTAINER}" \
  --net "${NETWORK}" \
  --cgroupns host \
  -i -t -d \
  --restart=always \
  -e "discovery.type=single-node" \
  -e "bootstrap.memory_lock=true" \
  -e "ingest.geoip.downloader.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms${HEAP_MB}m -Xmx${HEAP_MB}m -Dlog4j2.formatMsgNoLookups=true" \
  -e "indices.fielddata.cache.size=${FIELD_CACHE_SIZE}" \
  -e "indices.memory.index_buffer_size=${INDEX_BUFFER_SIZE}" \
  --ulimit "nofile=65535:65535" \
  --ulimit "memlock=-1:-1" \
  -v "${DATA_MOUNT}" \
  -v "/sys/fs/cgroup:/sys/fs/cgroup:rw" \
  "${IMAGE}" >/dev/null

if [ -n "${COMMUNITY_CONTAINER}" ]; then
  echo "[workspace-tune] restart ${COMMUNITY_CONTAINER}"
  docker restart "${COMMUNITY_CONTAINER}" >/dev/null 2>&1 || true
fi

echo "[workspace-tune] wait for Elasticsearch"
for _ in $(seq 1 "${WAIT_SECONDS}"); do
  state="$(docker inspect "${ES_CONTAINER}" --format '{{.State.Status}} {{.State.Restarting}} {{.State.ExitCode}}' 2>/dev/null || true)"
  if [ "${state}" = "running false 0" ]; then
    echo "[workspace-tune] Elasticsearch is stable"
    exit 0
  fi
  sleep 1
done

docker ps --filter "name=${ES_CONTAINER}" --format 'table {{.Names}}\t{{.Status}}'
docker logs --tail=80 "${ES_CONTAINER}" 2>&1 || true
fail "Elasticsearch did not stabilize in ${WAIT_SECONDS}s"
