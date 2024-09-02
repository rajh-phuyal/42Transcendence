#!/bin/bash
set -e

echo "STARTING MY ENTRYPOINT.SH..."

# Replace environment variables in SQL files before executing them
for file in /docker-entrypoint-initdb.d/*.sql; do
    envsubst < "$file" > "/tmp/$(basename $file)"
	echo "   Substituted environment variables in $file"
done

# Move substituted files back to the initdb.d directory
mv /tmp/*.sql /docker-entrypoint-initdb.d/

echo "STARTING MY ENTRYPOINT.SH...DONE"
echo "STARTING THE OFFICIAL ENTRYPOINT..."
exec docker-entrypoint.sh "$@"
echo "STARTING THE OFFICIAL ENTRYPOINT...DONE"
