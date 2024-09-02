#!/bin/bash

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Start the Django server
exec "$@"