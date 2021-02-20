FROM python:3.8-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY docker/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN ln -s /usr/local/bin/docker-entrypoint.sh / # backwards compat

COPY docker/wait-for /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for
RUN ln -s /usr/local/bin/wait-for / # backwards compat

COPY requirements.txt .

RUN apk update \
    && apk add --virtual build-deps \
        gcc \
        python3-dev \
        musl-dev \
        jpeg-dev \
        zlib-dev \
        libffi-dev \
    && apk add --no-cache mariadb-dev \
        freetype-dev \
        mysql-client

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del build-deps

WORKDIR /opt/app

COPY . .

VOLUME ["/opt/app/githon/static"]

ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 8000

CMD ["gunicorn", "githon.wsgi:application"]