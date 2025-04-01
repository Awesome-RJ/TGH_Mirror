#!/bin/bash

DATABASE_PATH="mongodb+srv://hunter123:hunter123@cluster0.iueac.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Update with your actual database file path

# Check if the database file exists
if [ ! -f "$DATABASE_PATH" ]; then
    echo "Error: Database file does not exist at $DATABASE_PATH"
    exit 1
fi

# Ensure the file has correct permissions
chmod 664 "$DATABASE_PATH"

# Execute the main command
exec "$@"
