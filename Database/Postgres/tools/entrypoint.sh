#!/bin/bash
set -e

# COLORS
RD='\033[0;31m'
GR='\033[0;32m'
NC='\033[0m'

echo "STARTING MY ENTRYPOINT.SH..."

# Replace environment variables in SQL files before executing them
for file in /docker-entrypoint-initdb.d/*.sql; do
    envsubst < "$file" > "/tmp/$(basename $file)"
	echo "   Substituted environment variables in $file"
done

# Move substituted files back to the initdb.d directory
mv /tmp/*.sql /docker-entrypoint-initdb.d/

# Initialize the database and start PostgreSQL in the background
echo "Starting PostgreSQL in the background..."
docker-entrypoint.sh postgres &

# Wait for PostgreSQL to be ready
until pg_isready -h localhost -p 5432; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 1
done
echo -e $GR "PostgreSQL is ready!" $NC

# Run the test for the root accounts
/tools/root_accounts.sh
status=$?

if [ $status -ne 0 ]; then
	echo -e $RD "Startup script failed with exit code $status. Exiting..." $NC
	# Stop the background PostgreSQL process if startup.sh fails
	killall postgres
	exit $status
fi

echo "STARTING MY ENTRYPOINT.SH...DONE"
# Bring PostgreSQL back to the foreground
wait -n
