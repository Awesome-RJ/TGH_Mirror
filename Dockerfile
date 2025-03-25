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

# Ensure tgh-env script is copied and executable
COPY tgh-env /usr/src/app/tgh-env
RUN chmod +x /usr/src/app/tgh-env

# Run tgh-env command
RUN /usr/src/app/tgh-env

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN /usr/src/app/tgh-env pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the default command to run the application
CMD ["bash", "start.sh"]
