FROM debian:bullseye-slim

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
 && curl -fsSLO https://www.python.org/ftp/python/2.4.6/Python-2.4.6.tgz \
 && tar -xzf Python-2.4.6.tgz \
 && cd Python-2.4.6 \
 && ./configure --prefix=${PY24_PREFIX} \
 && printf '\nzlib zlibmodule.c -I/usr/include -L/usr/lib/x86_64-linux-gnu -lz\n' >> Modules/Setup.local \
 && make -j"$(nproc)" \
 && make install \
 && ln -sf python2.4 ${PY24_PREFIX}/bin/python

RUN cd /tmp/build \
 && curl -fsSLO https://old.zope.dev/Products/Zope/2.9.10/Zope-2.9.10-final.tgz \
 && tar -xzf Zope-2.9.10-final.tgz \
 && cd Zope-2.9.10-final \
 && ./configure --prefix=${ZOPE_PREFIX} --with-python=${PY24_PREFIX}/bin/python2.4 \
 && make -j"$(nproc)" \
 && make install

RUN ${PY24_PREFIX}/bin/python2.4 ${ZOPE_PREFIX}/bin/mkzopeinstance.py --dir=${INSTANCE_HOME} --user=admin:admin

RUN groupadd -g 1000 zope \
 && useradd -m -u 1000 -g 1000 -s /bin/bash zope \
 && chown -R 1000:1000 ${INSTANCE_HOME} ${PY24_PREFIX} ${ZOPE_PREFIX}

COPY docker-legacy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /opt/naudoc
EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
