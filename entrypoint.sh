#!/bin/bash

DATABASE_URL="postgresql://tghbot_owner:npg_jae9mlh4kOMN@ep-shy-feather-a4hofch2-pooler.us-east-1.aws.neon.tech/tghbot?sslmode=require"  # Update with your actual database URL

# Ensure the database URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "Error: Database URL is not set"
    exit 1
fi

# Execute the main command
exec "$@"
