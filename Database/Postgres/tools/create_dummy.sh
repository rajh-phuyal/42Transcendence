#!/bin/bash

# ADD ALL TABLES INTO THIS ARRAY!
# (start from weak entity too not to break FK constraints)
# ------------------------------------------------------------------------------
ALL_TABLES=("barelyaschema.dev_user_data" 
			"barelyaschema.is_cool_with" 
			"barelyaschema.no_cool_with" 
			"barelyaschema.message" 
			"barelyaschema.conversation_member" 
			"barelyaschema.conversation" 
			"barelyaschema.user")

# Exit immediately if a command exits with a non-zero status
set -e

# Print header
print_header() {
  echo -e "\e[32m##############################################################\e[0m"
  echo -e "\e[32m# >>> $1 <<<\e[0m"
  echo -e "\e[32m##############################################################\e[0m"
}

# Function to display error message and exit
err_msg() {
  local message=$1
  echo -e "\e[31mDUMMY DATA ERROR: $message\e[0m"  # Print message in red
  exit 1
}

# Function to clean a table from all its rows
delete_old_data()
{
  local table_name=$1
  psql -U "$POSTGRES_USER" -w -d "$DB_NAME" -c "DELETE FROM $table_name;" \
  	|| err_msg "Failed to delete data from table '$table_name' due to foreign key constraints or other issues."
  printf "\e[31mDeleted old rows from table '%s' (if exist)...\e[0m\n" "$table_name"
}

# Function to insert dummy data into a table
insert_dummy()
{
  local table_name=$1
  local sql_query=$2
  printf "\e[33mInserting dummy data into table '%s'...\e[0m\n" "$table_name"
  psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "$sql_query" \
  	|| err_msg "Failed to insert dummy data into table '$table_name'."
  printf "\e[32mInserted dummy data into table '%s':\e[0m\n" "$table_name"
  psql -U $POSTGRES_USER -d $DB_NAME -c "SELECT * FROM $table_name;"
}

# Function to reset the sequence of a table's primary key
reset_sequence()
{
  local table_name=$1
  local sequence_name="${table_name}_id_seq"
  psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "SELECT setval('$sequence_name', COALESCE((SELECT MAX(id) FROM $table_name), 1) + 1, false);" \
  	|| err_msg "Failed to reset sequence for table '$table_name'."
  printf "\e[32mSequence for table '%s' reset to match the highest current ID...\e[0m\n" "$table_name"
}

# MAIN
#-------------------------------------------------------------------------------
print_header "Running 'create_dummy.sh'..."

print_header "DELETING OLD DATA..."
for table in "${ALL_TABLES[@]}"; do
    delete_old_data "$table"
done

print_header "INSERTING DUMMY DATA..."
TABLE_NAME="barelyaschema.user"
insert_dummy "$TABLE_NAME" \
	"INSERT INTO $TABLE_NAME (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES \
        (1, 'hashed_password_1', '2024-01-01 10:42:00+00', FALSE, 'arabelo-', 'Alê', 'Guedes', 'we dont use email', FALSE, FALSE, '2001-09-01 10:15:30+00'), \
        (2, 'hashed_password_2', '2024-02-01 11:42:01+00', FALSE, 'astein', 'Alex', 'Stein', 'we dont use email', FALSE, FALSE, '2002-09-01 10:15:30+00'), \
        (3, 'hashed_password_3', '2024-03-01 12:42:02+00', FALSE, 'anshovah', 'Anatolii', 'Shovah', 'we dont use email', FALSE, FALSE, '2003-09-01 10:15:30+00'), \
        (4, 'hashed_password_4', '2024-04-01 13:42:03+00', FALSE, 'fda-estr', 'Francisco', 'Inácio', 'we dont use email', FALSE, FALSE, '2004-09-01 10:15:30+00'), \
        (5, 'hashed_password_5', '2024-05-01 14:42:04+00', FALSE, 'rphuyal', 'Rajh', 'Phuyal', 'we dont use email', FALSE, FALSE, '2005-09-01 10:15:30+00');"

# TODO: add realtions to AI and the OVERLOARDS!
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

# Conversation 1: 1-2
# Conversation 2: 1-3
# Conversation 3: Group 1-2-3 name "barely a tournament chat" (not editable)
# Conversation 4: Group 1-2-3-4-5 name "barely ascrum room"
TABLE_NAME="barelyaschema.conversation"
insert_dummy "$TABLE_NAME" \
	"INSERT INTO $TABLE_NAME (id, name, is_group_conversation, is_editable) VALUES \
		(1, NULL, FALSE, TRUE), \
		(2, NULL, FALSE, TRUE), \
		(3, 'barely a tournament chat', TRUE, FALSE), \
		(4, 'barely a scrum room', TRUE, TRUE);"

TABLE_NAME="barelyaschema.conversation_member"
insert_dummy "$TABLE_NAME" \
	"INSERT INTO $TABLE_NAME (id, conversation_id, user_id) VALUES \
		(1, 1, 1), \
		(2, 1, 2), \
		(3, 2, 1), \
		(4, 2, 3), \
		(5, 3, 1), \
		(6, 3, 2), \
		(7, 3, 3), \
		(8, 4, 1), \
		(9, 4, 2), \
		(10, 4, 3), \
		(11, 4, 4), \
		(12, 4, 5);"

TABLE_NAME="barelyaschema.message"
insert_dummy "$TABLE_NAME" \
	"INSERT INTO $TABLE_NAME (id, user_id, conversation_id, content, created_at, seen_at) VALUES \
		(1, 1, 1, 'Hi Alex, how are you?', '2024-01-01 10:42:00+00', '2024-01-01 10:42:00+00'), \
		(2, 2, 1, 'Hi Alê, I am fine, thank you. How are you?', '2024-01-01 10:42:01+00', '2024-01-01 10:42:01+00'), \
		(3, 1, 1, 'I am fine too, thank you.', '2024-01-01 10:42:02+00', '2024-01-01 10:42:02+00'), \
		(4, 1, 2, 'Hi Anatolii, how are you?', '2024-01-01 10:42:03+00', '2024-01-01 10:42:03+00'), \
		(5, 3, 2, 'Hi Alê, I am fine, thank you. How are you?', '2024-01-01 10:42:04+00', '2024-01-01 10:42:04+00'), \
		(6, 1, 2, 'I am fine too, thank you.', '2024-01-01 10:42:05+00', '2024-01-01 10:42:05+00'), \
		(7, 1, 3, 'Lets play this tournament', '2024-01-01 10:42:06+00', NULL), \
		(8, 1, 3, 'Someone in this conversation???', '2024-01-01 10:45:06+00', NULL), \
		(9, 1, 3, 'Booooriiiiinnggg!!!', '2024-01-01 10:55:06+00', NULL), \
		(10, 2, 4, 'This is the scrum roooooom!! Are u guys here?', '2024-01-01 10:42:06+00', NULL), \
		(11, 1, 4, 'Hello :)', '2024-01-01 10:43:06+00', NULL), \
		(12, 3, 4, 'Yes, I am here', '2024-01-01 10:44:06+00', NULL), \
		(13, 4, 4, 'I am here too', '2024-01-01 10:44:10+00', NULL), \
		(14, 2, 4, 'Oye oye, what about u @rphuyal?', '2024-01-01 10:50:06+00', NULL), \
		(15, 5, 4, 'Me as well', '2024-01-01 10:51:06+00', NULL), \
		(16, 1, 4, 'Ok lets do this!', '2024-01-01 10:52:56+00',NULL);"

print_header "RESETING SEQUENCES..."
for table in "${ALL_TABLES[@]}"; do
    reset_sequence "$table"
done

print_header "Running 'create_dummy.sh'... DONE!"

printf "\033[1m > Check the wiki for details about the inserted dummy data:\033[0m\n"
printf "\033[1m > https://github.com/rajh-phuyal/42Transcendence/wiki/Database\033[0m\n"
