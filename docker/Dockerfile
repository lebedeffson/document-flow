FROM python:2.7-slim

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    INSTANCE_HOME=/opt/naudoc

RUN sed -i 's|deb.debian.org/debian|archive.debian.org/debian|g; s|security.debian.org/debian-security|archive.debian.org/debian-security|g' /etc/apt/sources.list \
 && sed -i '/buster-updates/d' /etc/apt/sources.list \
 && printf 'Acquire::Check-Valid-Until "false";\nAcquire::AllowInsecureRepositories "true";\n' > /etc/apt/apt.conf.d/99archive \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    libjpeg62-turbo-dev \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    netcat-openbsd \
    python-egenix-mxdatetime \
    python-ldap \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

COPY docker/zope-requirements-2.13.30.txt /tmp/zope-requirements-2.13.30.txt

RUN pip install --no-cache-dir "setuptools<45" "wheel<1" \
 && pip install --no-cache-dir -r /tmp/zope-requirements-2.13.30.txt \
 && pip install --no-cache-dir "Pillow==6.2.2"

RUN pip install --no-cache-dir "StructuredText==2.11.1" "Interface==2.11.1"

COPY docker/sitecustomize.py /usr/local/lib/python2.7/site-packages/sitecustomize.py
COPY docker/TALES.py /usr/local/lib/python2.7/site-packages/Products/PageTemplates/TALES.py

RUN mkzopeinstance --dir=${INSTANCE_HOME} --user=admin:admin

COPY naudoc_project/Products/TextIndexNG2 /tmp/TextIndexNG2
RUN cd /tmp/TextIndexNG2 \
 && python setup.py build \
 && python setup.py install \
 && rm -rf /tmp/TextIndexNG2 \
 && groupadd -g 1000 zope \
 && useradd -m -u 1000 -g 1000 -s /bin/bash zope \
 && chown -R 1000:1000 ${INSTANCE_HOME}

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /opt/naudoc
EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
