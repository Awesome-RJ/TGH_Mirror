#!/bin/bash

# Navigate to the project directory
cd /root/TGH_Mirror/tghbot

# Activate the virtual environment
source tgh-env/bin/activate 

# Install the requirements
/usr/src/app/tgh-env pip install -r requirements.txt

# Run the application
python3 update.py
python3 -m tghbot
