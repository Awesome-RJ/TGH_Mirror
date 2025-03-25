#!/bin/bash

# Navigate to the project directory
cd /root/TGH_Mirror/tghbot

# Activate the virtual environment
source tgh-env/bin/activate

# Edit the requirements.txt file to comment out or remove problematic packages (if needed)
nano requirements.txt

# Install the requirements
pip install -r requirements.txt

# Run the application
python3 update.py
python3 -m tghbot
