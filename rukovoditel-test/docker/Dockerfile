FROM php:8.2-apache

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    libcurl4-openssl-dev \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    libonig-dev \
    libpng-dev \
    libwebp-dev \
    libzip-dev \
    unzip \
    locales \
 && docker-php-ext-configure gd --with-freetype --with-jpeg --with-webp \
 && docker-php-ext-install -j"$(nproc)" \
    curl \
    gd \
    mysqli \
    mbstring \
    zip \
 && a2enmod rewrite \
 && sed -i 's|DocumentRoot /var/www/html|DocumentRoot /var/www/html|g' /etc/apache2/sites-available/000-default.conf \
 && rm -rf /var/lib/apt/lists/*

RUN echo "ru_RU.UTF-8 UTF-8" > /etc/locale.gen \
 && locale-gen \
 && update-locale LANG=ru_RU.UTF-8

RUN printf '%s\n' \
    'upload_max_filesize=64M' \
    'post_max_size=64M' \
    'memory_limit=512M' \
    'max_execution_time=120' \
    'date.timezone=Europe/Moscow' \
    > /usr/local/etc/php/conf.d/rukovoditel.ini

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /var/www/html

ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
