#!/bin/bash
set -e

echo "STARTING MY ENTRYPOINT.SH..."

# Replace environment variables in servers.json
envsubst < /pgadmin4/servers.json > /pgadmin4/servers_substituted.json
mv /pgadmin4/servers_substituted.json /pgadmin4/servers.json

# Replace environment variables in .pgpass
envsubst < /pgpassfile > /pgpassfile_substituted
mv /pgpassfile_substituted /pgpassfile
chmod 600 /pgpassfile

echo "STARTING MY ENTRYPOINT.SH...DONE"

# Pass control to the official pgAdmin entrypoint
exec /entrypoint.sh "$@"

