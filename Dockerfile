# Base stage
FROM ubuntu:22.04 

# Install required packages
RUN apt-get update && apt-get install -y \
    python3.13 \
    python3.13-venv \
    python3.13-pip \
    nano \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

COPY extract .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# RUN pip install --no-cache-dir setuptools

COPY tghbot/requirements.txt additional_requirements.txt
RUN pip install --no-cache-dir -r additional_requirements.txt


CMD ["bash", "start.sh"]
