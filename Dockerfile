FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    nano \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/TGH_Mirror/tghbot

# Copy requirements.txt to the tghbot directory
COPY requirements.txt ../requirements.txt

# Create and activate the virtual environment, then install dependencies
RUN python3 -m venv tgh-env \
    && source tgh-env/bin/activate \
    && pip install --no-cache-dir -r ../requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure start.sh is executable
RUN chmod +x /root/TGH_Mirror/start.sh

CMD ["bash", "start.sh"]
