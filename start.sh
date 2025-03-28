#!/bin/bash

# Start Aria2 in daemon mode
aria2c --enable-rpc --rpc-listen-all=true --rpc-allow-origin-all --daemon=true

# Your existing start commands
# ...

# Start your bot application
python3 -m tghbot
