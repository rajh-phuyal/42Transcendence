#!/bin/bash

# This script is used to create the database and the tables in the database
# The script should inside the database container

SCRIPT_NAME="populate_db.sh"
USER = $POSTGRES_USER
PASSWORD = $POSTGRES_PASSWORD
DB = "postgres"

psql -v ON_ERROR_STOP=1 -U "$USER" -d "$DB" <<-EOSQL
	
	INSERT INTO transcendence.users (username) VALUES ('anatolii', 'alex', 'francisco', 'rajh', 'joao');

	INSERT INTO is_cool_with (
		first_user_id
		, second_user_id
		, blocked_by_first
		, blocked_by_second
		, status)
	VALUES 
		(1, 2, false, false, 'pending'), ()
EOSQL