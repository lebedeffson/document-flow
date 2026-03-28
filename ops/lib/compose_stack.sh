#!/usr/bin/env bash

docflow_remove_stale_named_container() {
  local container_name="${1:-}"
  if [ -z "${container_name}" ]; then
    return 0
  fi

  if ! docker inspect "${container_name}" >/dev/null 2>&1; then
    return 0
  fi

  local status
  status="$(docker inspect -f '{{.State.Status}}' "${container_name}" 2>/dev/null || true)"
  if [ "${status}" = "running" ]; then
    return 0
  fi

  docker rm -f "${container_name}" >/dev/null 2>&1 || true
}

docflow_compose() {
  local project_dir="${1}"
  local project_name="${2}"
  local env_file="${3}"
  local compose_file="${4}"
  shift 4

  local cmd=(docker compose --project-directory "${project_dir}")
  if [ -n "${project_name}" ]; then
    cmd+=(-p "${project_name}")
  fi
  cmd+=(--env-file "${env_file}" -f "${compose_file}")
  cmd+=("$@")
  "${cmd[@]}"
}

docflow_stack_up() {
  local root_dir="${1}"
  local env_file="${2}"
  local build_mode="${3:-build}"
  local with_identity="${4:-0}"

  local up_args=(up -d)
  if [ "${build_mode}" = "build" ]; then
    up_args+=(--build)
  else
    up_args+=(--no-build)
  fi

  for stale_name in \
    "${NAUDOC_LEGACY_CONTAINER:-}" \
    "${RUKOVODITEL_DB_CONTAINER:-}" \
    "${RUKOVODITEL_CONTAINER_NAME:-}" \
    "${ONLYOFFICE_CONTAINER_NAME:-}" \
    "${RUKOVODITEL_SYNC_WORKER_CONTAINER_NAME:-}" \
    "${BRIDGE_CONTAINER:-}" \
    "${LDAP_CONTAINER_NAME:-}" \
    "${GATEWAY_CONTAINER_NAME:-}"; do
    docflow_remove_stale_named_container "${stale_name}"
  done

  docflow_compose "${root_dir}" "${NAUDOC_LEGACY_COMPOSE_PROJECT:-}" "${env_file}" "${root_dir}/docker-compose.legacy.yml" "${up_args[@]}"
  docflow_compose "${root_dir}/rukovoditel-test" "${RUKOVODITEL_COMPOSE_PROJECT_NAME:-}" "${env_file}" "${root_dir}/rukovoditel-test/docker-compose.yml" "${up_args[@]}"

  if [ "${with_identity}" = "1" ]; then
    docflow_compose "${root_dir}/middleware" "${MIDDLEWARE_COMPOSE_PROJECT_NAME:-}" "${env_file}" "${root_dir}/middleware/docker-compose.yml" --profile identity "${up_args[@]}"
  else
    docflow_compose "${root_dir}/middleware" "${MIDDLEWARE_COMPOSE_PROJECT_NAME:-}" "${env_file}" "${root_dir}/middleware/docker-compose.yml" "${up_args[@]}"
  fi

  docflow_compose "${root_dir}/gateway" "${GATEWAY_COMPOSE_PROJECT_NAME:-}" "${env_file}" "${root_dir}/gateway/docker-compose.yml" "${up_args[@]}"
}

docflow_stack_down() {
  local root_dir="${1}"
  local env_file="${2}"
  local with_identity="${3:-1}"

  docflow_compose "${root_dir}/gateway" "${GATEWAY_COMPOSE_PROJECT_NAME:-}" "${env_file}" "${root_dir}/gateway/docker-compose.yml" down
  if [ "${with_identity}" = "1" ]; then
    docflow_compose "${root_dir}/middleware" "${MIDDLEWARE_COMPOSE_PROJECT_NAME:-}" "${env_file}" "${root_dir}/middleware/docker-compose.yml" --profile identity down
  else
    docflow_compose "${root_dir}/middleware" "${MIDDLEWARE_COMPOSE_PROJECT_NAME:-}" "${env_file}" "${root_dir}/middleware/docker-compose.yml" down
  fi
  docflow_compose "${root_dir}/rukovoditel-test" "${RUKOVODITEL_COMPOSE_PROJECT_NAME:-}" "${env_file}" "${root_dir}/rukovoditel-test/docker-compose.yml" down
  docflow_compose "${root_dir}" "${NAUDOC_LEGACY_COMPOSE_PROJECT:-}" "${env_file}" "${root_dir}/docker-compose.legacy.yml" down
}
