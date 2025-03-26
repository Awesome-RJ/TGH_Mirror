# Base stage
FROM ubuntu:22.04 AS base

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

# Second stage for additional requirements
FROM base AS additional

# Ensure setuptools is installed
RUN pip install --no-cache-dir setuptools

COPY tghbot/requirements.txt additional_requirements.txt
RUN pip install --no-cache-dir -r additional_requirements.txt

# Final stage
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

# Copy from the additional stage
COPY --from=additional /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=additional /usr/local/bin /usr/local/bin

COPY . .

CMD ["bash", "start.sh"]
