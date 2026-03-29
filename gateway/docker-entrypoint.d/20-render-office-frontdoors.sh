#!/bin/sh
set -eu

SNIPPET_DIR="/etc/nginx/snippets"

parse_url_field() {
  url="${1:-}"
  field="${2:-}"

  case "${field}" in
    scheme)
      printf '%s' "${url}" | sed -E 's#^([A-Za-z][A-Za-z0-9+.-]*)://.*#\1#'
      ;;
    netloc)
      printf '%s' "${url}" | sed -E 's#^[A-Za-z][A-Za-z0-9+.-]*://([^/]+).*$#\1#'
      ;;
    hostname)
      netloc="$(parse_url_field "${url}" netloc)"
      printf '%s' "${netloc%%:*}"
      ;;
    path)
      path="$(printf '%s' "${url}" | sed -E 's#^[A-Za-z][A-Za-z0-9+.-]*://[^/]+(.*)$#\1#')"
      if [ -z "${path}" ]; then
        path="/"
      fi
      printf '%s' "${path}"
      ;;
    *)
      printf ''
      ;;
  esac
}

render_frontdoor() {
  service="$1"
  target_url="${2:-}"
  snippet_path="${SNIPPET_DIR}/${service}_frontdoor.conf"

  mkdir -p "${SNIPPET_DIR}"

  if [ -n "${target_url}" ]; then
    target_url="${target_url%/}"
    target_scheme="$(parse_url_field "${target_url}" scheme)"
    target_hostname="$(parse_url_field "${target_url}" hostname)"
    target_netloc="$(parse_url_field "${target_url}" netloc)"

    cat > "${snippet_path}" <<EOF
location /${service}/ {
    if (\$arg_shell = "1") {
        rewrite ^ /index.php?module=dashboard/ecosystem&service=${service}&\$args last;
    }

    proxy_http_version 1.1;
    proxy_ssl_server_name on;
    proxy_set_header Host ${target_netloc};
    proxy_set_header X-Forwarded-Proto https;
    proxy_set_header X-Forwarded-Host ${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX};
    proxy_set_header X-Forwarded-Port ${EXTERNAL_HTTPS_PORT};
    proxy_set_header X-Forwarded-Prefix /${service};
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection \$connection_upgrade;
    proxy_cookie_path / /${service}/;
    proxy_redirect ${target_url}/ /${service}/;
    proxy_redirect ${target_url} /${service};
    proxy_redirect http://${target_netloc}/ /${service}/;
    proxy_redirect https://${target_netloc}/ /${service}/;
    proxy_redirect http://${target_hostname}/ /${service}/;
    proxy_redirect https://${target_hostname}/ /${service}/;
    proxy_buffering off;
    proxy_pass ${target_url}/;

    sub_filter_once off;
    sub_filter_types text/html text/css application/javascript application/x-javascript text/javascript application/json;
    sub_filter 'href="/' 'href="/${service}/';
    sub_filter 'src="/' 'src="/${service}/';
    sub_filter 'action="/' 'action="/${service}/';
    sub_filter 'content="/' 'content="/${service}/';
    sub_filter 'url(/' 'url(/${service}/';
    sub_filter 'url("/' 'url("/${service}/';
    sub_filter "url('/" "url('/${service}/";
    sub_filter '${target_url}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/${service}/';
    sub_filter '${target_scheme}://${target_netloc}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/${service}/';
    sub_filter '${target_scheme}://${target_hostname}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/${service}/';
}
EOF
    return 0
  fi

  cat > "${snippet_path}" <<EOF
location /${service}/ {
    rewrite ^ /index.php?module=dashboard/ecosystem&service=${service}&\$args last;
}
EOF
}

render_frontdoor "docspace" "${DOCSPACE_TARGET_URL:-}"
render_frontdoor "workspace" "${WORKSPACE_TARGET_URL:-}"
