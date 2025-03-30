FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
RUN mkdir ./app
RUN chmod 777 ./app
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata

RUN apt -qq update --fix-missing && \
    apt -qq install -y git \
    aria2 \
    wget \
    curl \
    busybox \
    unzip \
    unrar \
    tar \
    python3 \
    ffmpeg \
    python3-pip \
    p7zip-full \
    p7zip-rar
# Copy the requirements files
COPY requirements.txt .
COPY tghbot/requirements.txt ./tghbot/

# Install setuptools
RUN pip3 install --upgrade setuptools wheel
# Install any needed packages specified in requirements.txt and tghbot/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir -r tghbot/requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the default command to execute
# RUN bash extract.sh

CMD ["bash", "start.sh"]
