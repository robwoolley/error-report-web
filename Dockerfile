# See README for how to use this.
# Based on Dockerfile for layerindex-web

FROM ubuntu:jammy
LABEL maintainer="Rob Woolley <rob.woolley@windriver.com>"

ENV PYTHONUNBUFFERED=1 \
    LANGUAGE=en_US \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LC_CTYPE=en_US.UTF-8
## Uncomment to set proxy ENVVARS within container
#ENV http_proxy http://your.proxy.server:port
#ENV https_proxy https://your.proxy.server:port
#ENV no_proxy localhost,127.0.0.0/8

# NOTE: we don't purge gcc below as we have some places in the OE metadata that look for it

COPY requirements.txt /
RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get install -y locales \
    && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
        && locale-gen en_US.UTF-8 \
        && update-locale \
    && apt-get install -y --no-install-recommends \
	autoconf \
	g++ \
	gcc \
	make \
	python2 \
	python3-pip \
	python3-mysqldb \
	python3-dev \
	python3-wheel \
	zlib1g-dev \
	libfreetype6-dev \
	libjpeg-dev \
	libmariadb-dev-compat \
	netcat-openbsd \
	curl \
	wget \
	git \
	vim \
	rpm2cpio \
	rpm \
	cpio \
    && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
	&& locale-gen en_US.UTF-8 \
	&& update-locale \
    && pip3 install gunicorn \
    && pip3 install setuptools \
    && pip3 install -r /requirements.txt \
    && apt-get purge -y autoconf g++ make python3-dev libjpeg-dev \
	&& apt-get autoremove -y \
	&& rm -rf /var/lib/apt/lists/* \
	&& apt-get clean

COPY . /opt/errorreport
COPY docker/migrate.sh /opt/migrate.sh

# Start Gunicorn
WORKDIR /opt/errorreport
RUN /opt/migrate.sh

CMD ["/usr/local/bin/gunicorn", "wsgi:application", "--workers=4", "--bind=:5000", "--timeout=60", "--log-level=debug", "--chdir=/opt/errorreport"]
