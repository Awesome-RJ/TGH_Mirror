FROM ubuntu:20.04


RUN mkdir ./app
RUN chmod 777 ./app
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    python3-pip \
    libffi-dev \
    git \
    sabnzbdplus \
    && rm -rf /var/lib/apt/lists/*

RUN . $VIRTUAL_ENV/bin/activate && \
    pip3 install --break-system-packages --no-cache-dir \
    setuptools \
    pymongo \
    motor \
    uvloop \
    cython \
    wheel



apt-get install -y software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update
    apt-get install -y python3.12 python3.12-dev python3.12-venv python3-pip libpython3.12 libpython3.12-dev
apt-get install -y --no-install-recommends \
        apt-utils aria2 curl zstd git libmagic-dev \
        locales mediainfo neofetch p7zip-full \
        p7zip-rar tzdata wget autoconf automake \
        build-essential cmake g++ gcc gettext \
        gpg-agent intltool libtool make unzip zip \
        libcurl4-openssl-dev libsodium-dev libssl-dev \
        libcrypto++-dev libc-ares-dev libsqlite3-dev \
        libfreeimage-dev swig libboost-all-dev \
        libpthread-stubs0-dev zlib1g-dev

RUN wget https://rclone.org/install.sh
RUN bash install.sh

RUN mkdir /app/gautam
RUN wget -O /app/gautam/gclone.gz https://git.io/JJMSG
RUN gzip -d /app/gautam/gclone.gz
RUN chmod 0775 /app/gautam/gclone

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
#RUN chmod +x extract
CMD ["bash","start.sh"]
