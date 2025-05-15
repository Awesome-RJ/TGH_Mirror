FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tzdata \
    python3 \
    python3-venv \
    python3-pip \
    git \
    aria2 \
    wget \
    curl \
    unzip \
    unrar \
    tar \
    ffmpeg \
    p7zip-full \
    p7zip-rar \
    qbittorrent-nox \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirement files and install Python packages
COPY requirements.txt .
RUN pip3 install --upgrade pip setuptools wheel \
    && pip3 install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Make scripts executable
RUN chmod +x aria.sh entrypoint.sh start.sh

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Default command
CMD ["bash", "start.sh"]
