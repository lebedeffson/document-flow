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
    target_origin="${target_scheme}://${target_netloc}"
    target_port=""
    proxy_host_header="${target_netloc}"
    forwarded_proto_line='    proxy_set_header X-Forwarded-Proto https;'
    forwarded_host_line="    proxy_set_header X-Forwarded-Host ${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX};"
    if printf '%s' "${target_netloc}" | grep -q ':'; then
      target_port="${target_netloc##*:}"
    fi
    cookie_path="/${service}/"

    if [ "${service}" = "workspace" ]; then
      cookie_path="/"
    fi

    if [ "${service}" = "docspace" ]; then
      proxy_host_header="${SERVER_NAME}"
      if [ -n "${target_port}" ]; then
        proxy_host_header="${SERVER_NAME}:${target_port}"
      fi
      forwarded_proto_line=""
      forwarded_host_line=""
    fi

    cat > "${snippet_path}" <<EOF
EOF
    if [ "${service}" = "workspace" ]; then
      cat >> "${snippet_path}" <<EOF
location = /Wizard.aspx {
    return 302 /workspace/Wizard.aspx;
}

location ~* ^/(?:Auth\.aspx|Confirm\.aspx|Wizard\.aspx|UserControls(?:/|$)|addons(?:/|$)|ajaxpro(?:/|$)|api/2\.0(?:/|$)|clientscript(?:/|$)|discbundle(?:/|$)|products(?:/|$)|services(?:/|$)|skins(?:/|$)|socketio(?:/|$)) {
    proxy_http_version 1.1;
    proxy_set_header Accept-Encoding "";
    proxy_ssl_server_name on;
    proxy_set_header Host ${target_netloc};
    proxy_set_header X-Forwarded-Proto https;
    proxy_set_header X-Forwarded-Host ${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX};
    proxy_set_header X-Forwarded-Port ${EXTERNAL_HTTPS_PORT};
    proxy_set_header X-Forwarded-Prefix /workspace;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection \$connection_upgrade;
    proxy_cookie_path / /;
    proxy_redirect ${target_url}/ /workspace/;
    proxy_redirect ${target_url} /workspace;
    proxy_redirect ${target_origin}/ /workspace/;
    proxy_redirect http://${target_netloc}/ /workspace/;
    proxy_redirect https://${target_netloc}/ /workspace/;
    proxy_redirect http://${target_hostname}/ /workspace/;
    proxy_redirect https://${target_hostname}/ /workspace/;
    proxy_redirect / /workspace/;
    proxy_redirect ~^(/.+)\$ /workspace\$1;
    proxy_buffering off;
    proxy_pass ${target_origin};
}

EOF
    fi

    if [ "${service}" = "docspace" ]; then
      cat >> "${snippet_path}" <<EOF
location ~* ^/(?:api/2\.0(?:/|$)|files(?:/|$)|locales(?:/|$)|login(?:/|$)|wizard(?:/|$)|portal-settings(?:/|$)|logo\.ashx$|socket\.io(?:/|$)|static(?:/|$)) {
    proxy_http_version 1.1;
    proxy_set_header Accept-Encoding "";
    proxy_ssl_server_name on;
    proxy_set_header Host ${proxy_host_header};
${forwarded_proto_line}
${forwarded_host_line}
    proxy_set_header X-Forwarded-Port ${EXTERNAL_HTTPS_PORT};
    proxy_set_header X-Forwarded-Prefix /docspace;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection \$connection_upgrade;
    proxy_cookie_path / /docspace/;
    proxy_redirect ${target_url}/ /docspace/;
    proxy_redirect ${target_url} /docspace;
    proxy_redirect ${target_origin}/ /docspace/;
    proxy_redirect http://${target_netloc}/ /docspace/;
    proxy_redirect https://${target_netloc}/ /docspace/;
    proxy_redirect http://${target_hostname}/ /docspace/;
    proxy_redirect https://${target_hostname}/ /docspace/;
    proxy_redirect / /docspace/;
    proxy_redirect ~^(/.+)\$ /docspace\$1;
    proxy_buffering off;
    proxy_pass ${target_origin};

    sub_filter_once off;
    sub_filter_types text/html text/css application/javascript application/x-javascript text/javascript application/json;
    sub_filter 'href="/' 'href="/docspace/';
    sub_filter "href='/" "href='/docspace/";
    sub_filter 'src="/' 'src="/docspace/';
    sub_filter "src='/" "src='/docspace/";
    sub_filter 'action="/' 'action="/docspace/';
    sub_filter "action='/" "action='/docspace/";
    sub_filter 'content="/' 'content="/docspace/';
    sub_filter "content='/" "content='/docspace/";
    sub_filter 'url(/' 'url(/docspace/';
    sub_filter 'url("/' 'url("/docspace/';
    sub_filter "url('/" "url('/docspace/";
    sub_filter '"redirectURL":"/wizard"' '"redirectURL":"/docspace/wizard"';
    sub_filter '"redirectURL":"/login"' '"redirectURL":"/docspace/login"';
    sub_filter '${target_url}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/docspace/';
    sub_filter '${target_scheme}://${target_netloc}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/docspace/';
    sub_filter '${target_scheme}://${target_hostname}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/docspace/';
    sub_filter 'http://${proxy_host_header}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/docspace/';
    sub_filter 'https://${proxy_host_header}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/docspace/';
    sub_filter 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/docspace/';
    sub_filter 'http://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/docspace/';
    sub_filter 'http://${SERVER_NAME}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/docspace/';
}

EOF
    fi

    cat >> "${snippet_path}" <<EOF
location /${service}/ {
    if (\$arg_shell = "1") {
        rewrite ^ /index.php?module=dashboard/ecosystem&service=${service}&\$args last;
    }

EOF
    if [ "${service}" = "docspace" ]; then
      cat >> "${snippet_path}" <<EOF
    if (\$uri = /docspace/) {
        return 302 /docspace/login;
    }

EOF
    fi
    cat >> "${snippet_path}" <<EOF

    proxy_http_version 1.1;
    proxy_set_header Accept-Encoding "";
    proxy_ssl_server_name on;
    proxy_set_header Host ${proxy_host_header};
${forwarded_proto_line}
${forwarded_host_line}
    proxy_set_header X-Forwarded-Port ${EXTERNAL_HTTPS_PORT};
    proxy_set_header X-Forwarded-Prefix /${service};
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection \$connection_upgrade;
    proxy_cookie_path / ${cookie_path};
    proxy_redirect ${target_url}/ /${service}/;
    proxy_redirect ${target_url} /${service};
    proxy_redirect http://${target_netloc}/ /${service}/;
    proxy_redirect https://${target_netloc}/ /${service}/;
    proxy_redirect http://${target_hostname}/ /${service}/;
    proxy_redirect https://${target_hostname}/ /${service}/;
    proxy_redirect / /${service}/;
    proxy_redirect ~^(/.+)\$ /${service}\$1;
    proxy_buffering off;
    proxy_pass ${target_url}/;

    sub_filter_once off;
    sub_filter_types text/html text/css application/javascript application/x-javascript text/javascript application/json;
    sub_filter 'href="/' 'href="/${service}/';
    sub_filter "href='/" "href='/${service}/";
    sub_filter 'src="/' 'src="/${service}/';
    sub_filter "src='/" "src='/${service}/";
    sub_filter 'action="/' 'action="/${service}/';
    sub_filter "action='/" "action='/${service}/";
    sub_filter 'content="/' 'content="/${service}/';
    sub_filter "content='/" "content='/${service}/";
    sub_filter 'url(/' 'url(/${service}/';
    sub_filter 'url("/' 'url("/${service}/';
    sub_filter "url('/" "url('/${service}/";
    sub_filter '"redirectURL":"/wizard"' '"redirectURL":"/${service}/wizard"';
    sub_filter '"redirectURL":"/login"' '"redirectURL":"/${service}/login"';
    sub_filter '${target_url}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/${service}/';
    sub_filter '${target_scheme}://${target_netloc}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/${service}/';
    sub_filter '${target_scheme}://${target_hostname}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/${service}/';
    sub_filter 'http://${proxy_host_header}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/${service}/';
    sub_filter 'https://${proxy_host_header}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/${service}/';
    sub_filter 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/${service}/';
    sub_filter 'http://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/${service}/';
    sub_filter 'http://${SERVER_NAME}/' 'https://${SERVER_NAME}${EXTERNAL_HTTPS_SUFFIX}/${service}/';
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
