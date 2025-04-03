#!/bin/bash

DATABASE_PATH="postgresql://tghbot_owner:npg_jae9mlh4kOMN@ep-shy-feather-a4hofch2-pooler.us-east-1.aws.neon.tech/tghbot?sslmode=require"  # Update with your actual database file path

# Check if the database file exists
if [ ! -f "$DATABASE_PATH" ]; then
    echo "Error: Database file does not exist at $DATABASE_PATH"
    exit 1
fi

# Ensure the file has correct permissions
chmod 664 "$DATABASE_PATH"

# Execute the main command
exec "$@"
