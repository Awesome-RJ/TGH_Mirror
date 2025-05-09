FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=noninteractive

# Set the timezone environment variable (adjust to your desired timezone)
ENV TZ=America/New_York

# Install tzdata package if not already installed
RUN apt-get update && apt-get install -y tzdata

# Create and set permissions for the application directory
RUN mkdir ./app
RUN chmod 777 ./app
WORKDIR /app

RUN apt -qq update --fix-missing && \
    apt -qq install -y git \
    aria2 \
    wget \
    curl \
    unzip \
    unrar \
    tar \
    python3 \
    ffmpeg \
    python3-pip \
    p7zip-full \
    p7zip-rar \
    qbittorrent-nox  # Add this line to install qbittorrent-nox

# Copy the requirements files
COPY requirements.txt .
# COPY tghbot/requirements.txt ./tghbot/

# Install setuptools
RUN pip3 install --upgrade setuptools wheel

# Install any needed packages specified in requirements.txt and tghbot/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
# RUN pip3 install --no-cache-dir -r tghbot/requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Update permissions for aria.sh
RUN chmod +x aria.sh

# Check and ensure the database file exists and has correct permissions
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Set the default command to execute
CMD ["bash", "start.sh"]
