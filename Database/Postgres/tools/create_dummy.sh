#!/bin/bash

# Function to clean a table from all its rows
delete_old_data()
{
  local table_name=$1
  psql -U "$POSTGRES_USER" -w -d "$DB_NAME" -c "DELETE FROM $table_name;"
  printf "\e[31mDeleted old rows from table '%s' (if exist)...\e[0m\n\n" "$table_name"
}

# Function to insert dummy data into a table
insert_dummy()
{
  local table_name=$1
  local sql_query=$2
  printf "\e[33mInserting dummy data into table '%s'...\e[0m\n" "$table_name"
  psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "$sql_query"
  printf "\e[32mInserted dummy data into table '%s':\e[0m\n" "$table_name"
  psql -U $POSTGRES_USER -d $DB_NAME -c "SELECT * FROM $table_name;"
}

# MAIN
#-------------------------------------------------------------------------------
printf "\e[32mStarting to create dummy data...\e[0m\n\n"

# STEP 1: Delete old Data (start from weak entity too not to break FK constraints)
delete_old_data "barelyaschema.is_cool_with"
delete_old_data "barelyaschema.no_cool_with"
delete_old_data "barelyaschema.user"

# STEP 2: Insert dummy data
TABLE_NAME="barelyaschema.user"
insert_dummy "$TABLE_NAME" \
	"INSERT INTO $TABLE_NAME (id, username, pswd) VALUES \
    	(1, 'Alê', 'hashed_password_1'), \
    	(2, 'Alex', 'hashed_password_2'), \
    	(3, 'Anatolii', 'hashed_password_3'), \
    	(4, 'Francisco', 'hashed_password_4'), \
    	(5, 'Rajh', 'hashed_password_5');"

TABLE_NAME="barelyaschema.is_cool_with"
insert_dummy "$TABLE_NAME" \
	"INSERT INTO $TABLE_NAME (id, requester_id, requestee_id, status) VALUES \
		(1, 1, 2, 'accepted'), \
		(2, 1, 3, 'accepted'), \
		(3, 1, 4, 'accepted'), \
		(4, 1, 5, 'accepted'), \
		(5, 2, 3, 'accepted'), \
		(6, 2, 4, 'pending'), \
		(7, 5, 4, 'pending'), \
		(8, 2, 5, 'rejected');"


TABLE_NAME="barelyaschema.no_cool_with"
insert_dummy "$TABLE_NAME" \
	"INSERT INTO $TABLE_NAME (id, blocker_id, blocked_id) VALUES \
		(1, 3, 1), \
		(2, 3, 4), \
		(3, 4, 3);"

printf "\e[32mStarting to create dummy data...DONE\e[0m\n\n"
# TODO: Link GitHub Wiki Image here!