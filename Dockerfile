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

# Copy the requirements files
COPY requirements.txt .
COPY tghbot/requirements.txt ./tghbot/

# Install setuptools
RUN pip install --upgrade setuptools

# Install any needed packages specified in requirements.txt and tghbot/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r tghbot/requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the default command to execute
CMD ["bash", "start.sh"]
