#!/bin/bash

DATABASE_PATH="/path/to/your/database/file.db"  # Update with your actual database file path

# Check if the database file exists
if [ ! -f "$DATABASE_PATH" ]; then
    echo "Error: Database file does not exist at $DATABASE_PATH"
    exit 1
fi

# Ensure the file has correct permissions
chmod 664 "$DATABASE_PATH"

# Execute the main command
exec "$@"
