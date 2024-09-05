#!/bin/bash

# Apply database migrations
echo 'Starting 'python manage.py makemigrations'' > migration_logs.txt
echo '================' >> migration_logs.txt
python manage.py makemigrations >> migration_logs.txt
echo 'Starting 'python manage.py migrate'' >> migration_logs.txt
python manage.py migrate >> migration_logs.txt

# Start the Django server
exec "$@"