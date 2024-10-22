#!/bin/bash

# Apply database migrations
echo 'Starting 'python manage.py makemigrations'' > migration_logs.log
echo '================' >> migration_logs.log
python manage.py makemigrations >> migration_logs.log
echo 'Starting 'python manage.py migrate'' >> migration_logs.log
python manage.py migrate >> migration_logs.log

# Start the Django server
exec "$@"