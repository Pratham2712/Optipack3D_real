#!/bin/sh

# Apply database migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Execute the command passed to the container
exec "$@"