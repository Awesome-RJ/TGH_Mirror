#!/bin/bash

DATABASE_URL="mongodb+srv://hunter123:hunter123@cluster0.iueac.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Update with your actual database URL

# Attempt to connect to the database
if ! mongo "$DATABASE_URL" --eval "db.stats()" >/dev/null 2>&1; then
    echo "Error: Unable to connect to the database at $DATABASE_URL"
    exit 1
fi

# Execute the main command
exec "$@"
