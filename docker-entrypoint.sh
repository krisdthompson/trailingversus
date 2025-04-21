#!/bin/bash

# Check if Django project exists
if [ ! -f "manage.py" ]; then
    echo "No Django project found. Waiting..."
    tail -f /dev/null
else
    # Apply database migrations
    echo "Applying database migrations..."
    python manage.py makemigrations
    python manage.py migrate


    # Collect static files
    echo "Collecting static files..."
    python manage.py collectstatic --noinput

# now run CMD from docker compose config
echo "Running $@"
exec "$@" 

fi 