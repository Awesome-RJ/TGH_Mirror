FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    nano \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

RUN python3 -m venv tgh-env 

COPY requirements.txt .
RUN tgh-env/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "start.sh"]
