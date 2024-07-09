#!/bin/bash

# This script is used to create the database and the tables in the database
# The script should inside the database container

SCRIPT_NAME="populate_db.sh"
USER = $POSTGRES_USER
PASSWORD = $POSTGRES_PASSWORD
DB = "postgres"

psql -v ON_ERROR_STOP=1 -U "$USER" -d "$DB" <<-EOSQL
	-- the script to populate the database will be here
EOSQL