FROM debian:bullseye-slim

ARG PY24_SOURCE_URL=https://www.python.org/ftp/python/2.4.6/Python-2.4.6.tgz
ARG ZOPE_SOURCE_URL=https://old.zope.dev/Products/Zope/2.9.10/Zope-2.9.10-final.tgz
ARG ZOPE_SOURCE_FALLBACK_URL=https://codeload.github.com/zopefoundation/Zope/tar.gz/refs/tags/2.9.10

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PY24_PREFIX=/opt/python2.4 \
    ZOPE_PREFIX=/opt/zope \
    INSTANCE_HOME=/opt/naudoc

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    libbz2-dev \
    libdb-dev \
    libexpat1-dev \
    libffi-dev \
    libgdbm-dev \
    libjpeg-dev \
    libncurses5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libz-dev \
    rsync \
    tk-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /tmp/build \
 && cd /tmp/build \
 && curl --fail --show-error --location \
      --retry 6 --retry-delay 5 --retry-all-errors \
      --connect-timeout 30 --max-time 1800 \
      -o Python-2.4.6.tgz "${PY24_SOURCE_URL}" \
 && tar -xzf Python-2.4.6.tgz \
 && cd Python-2.4.6 \
 && ./configure --prefix=${PY24_PREFIX} \
 && printf '\nzlib zlibmodule.c -I/usr/include -L/usr/lib/x86_64-linux-gnu -lz\n' >> Modules/Setup.local \
 && make -j"$(nproc)" \
 && make install \
 && ln -sf python2.4 ${PY24_PREFIX}/bin/python

RUN cd /tmp/build \
 && rm -f Zope-2.9.10-final.tgz \
 && if ! curl --fail --show-error --location \
      --retry 6 --retry-delay 5 --retry-all-errors \
      --connect-timeout 30 --max-time 1800 \
      -o Zope-2.9.10-final.tgz "${ZOPE_SOURCE_URL}"; then \
      echo "Primary Zope source failed, falling back to GitHub tag archive" >&2; \
      curl --fail --show-error --location \
        --retry 6 --retry-delay 5 --retry-all-errors \
        --connect-timeout 30 --max-time 1800 \
        -o Zope-2.9.10-final.tgz "${ZOPE_SOURCE_FALLBACK_URL}"; \
    fi \
 && tar -xzf Zope-2.9.10-final.tgz \
 && if [ -d Zope-2.9.10-final ]; then cd Zope-2.9.10-final; else cd Zope-2.9.10; fi \
 && ./configure --prefix=${ZOPE_PREFIX} --with-python=${PY24_PREFIX}/bin/python2.4 \
 && make -j"$(nproc)" \
 && make install

RUN ${PY24_PREFIX}/bin/python2.4 ${ZOPE_PREFIX}/bin/mkzopeinstance.py --dir=${INSTANCE_HOME} --user=admin:admin

RUN groupadd -g 1000 zope \
 && useradd -m -u 1000 -g 1000 -s /bin/bash zope \
 && chown -R 1000:1000 ${INSTANCE_HOME} ${PY24_PREFIX} ${ZOPE_PREFIX}

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /opt/naudoc
EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
