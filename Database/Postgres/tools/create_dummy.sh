#!/bin/bash
# ------------------------------------------------------------------------------
# ADD ALL TABLES INTO THIS ARRAY!
# (start from weak entity too not to break FK constraints)
# ------------------------------------------------------------------------------
ALL_TABLES=("barelyaschema.dev_user_data"
            "barelyaschema.game_member"
            "barelyaschema.game"
            "barelyaschema.tournament_member"
            "barelyaschema.tournament"
			"barelyaschema.is_cool_with" 
			"barelyaschema.no_cool_with" 
			"barelyaschema.message" 
			"barelyaschema.conversation_member" 
			"barelyaschema.conversation" 
			"barelyaschema.user")
# Fixed UserIDs:
ID_OVERLOARDS=1
ID_AI=2

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

#-------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------
print_header "Running 'create_dummy.sh'..."

print_header "DELETING OLD DATA..."
for table in "${ALL_TABLES[@]}"; do
    delete_old_data "$table"
done

# Important here we need to create the root users first!
print_header "INSERTING ROOT USERS..."
/tools/root_accounts.sh

print_header "INSERTING DUMMY DATA..."
TABLE_NAME="barelyaschema.user"
insert_dummy "$TABLE_NAME"                                                                                                                                                                                                                              \
	"INSERT INTO $TABLE_NAME                                                                                                                                                                                                                            \
        (id,    password,               last_login,                 is_superuser,   username,   first_name,     last_name,  email,                  is_staff,   is_active,  date_joined,                avatar_path) VALUES                             \
        (3,     'hashed_password_1',    '2024-01-01 10:42:00+00',   FALSE,          'static-arabelo-', 'Alê',          'Guedes',   'we dont use email',    FALSE,      FALSE,      '2001-09-01 10:15:30+00',   '4d39f530-68c8-42eb-ad28-45445424da5b.png'),    \
        (4,     'hashed_password_2',    '2024-02-01 11:42:01+00',   FALSE,          'static-astein',   'Alex',         'Stein',    'we dont use email',    FALSE,      FALSE,      '2002-09-01 10:15:30+00',   '73d3a3c0-f3ef-43a1-bdce-d798cb286f27.png'),    \
        (5,     'hashed_password_3',    '2024-03-01 12:42:02+00',   FALSE,          'static-anshovah', 'Anatolii',     'Shovah',   'we dont use email',    FALSE,      FALSE,      '2003-09-01 10:15:30+00',   '1e3751c5-5e47-45f2-9967-111fd26a6be8.png'),    \
        (6,     'hashed_password_4',    '2024-04-01 13:42:03+00',   FALSE,          'static-fda-estr', 'Francisco',    'Inácio',   'we dont use email',    FALSE,      FALSE,      '2004-09-01 10:15:30+00',   'fe468ade-12ed-4045-80a7-7d3e45be997e.png'),    \
        (7,     'hashed_password_5',    '2024-05-01 14:42:04+00',   FALSE,          'static-rphuyal',  'Rajh',         'Phuyal',   'we dont use email',    FALSE,      FALSE,      '2005-09-01 10:15:30+00',   'dd6e8101-fde8-469a-97dc-6b8bb9e8296e.png');"

TABLE_NAME="barelyaschema.is_cool_with"
insert_dummy "$TABLE_NAME"                                      \
	"INSERT INTO $TABLE_NAME                                    \
        (id,    requester_id,   requestee_id, status) VALUES    \
		(1,     $ID_AI,         3,          'accepted'),        \
		(2,     $ID_AI,         4,          'accepted'),        \
		(3,     $ID_AI,         5,          'accepted'),        \
		(4,     $ID_AI,         6,          'accepted'),        \
		(5,     $ID_AI,         7,          'accepted'),        \
		(6,     3,              4,          'accepted'),        \
		(7,     3,              5,          'accepted'),        \
		(8,     3,              6,          'accepted'),        \
		(9,     3,              7,          'accepted'),        \
		(10,    4,              5,          'accepted'),        \
		(11,    4,              6,          'pending'),         \
		(12,    7,              6,          'pending');"

TABLE_NAME="barelyaschema.no_cool_with"
insert_dummy "$TABLE_NAME"                          \
	"INSERT INTO $TABLE_NAME                        \
        (id,    blocker_id,     blocked_id) VALUES  \
		(1,     $ID_OVERLOARDS, 3),                 \
		(2,     $ID_OVERLOARDS, 4),                 \
		(3,     $ID_OVERLOARDS, 5),                 \
		(4,     $ID_OVERLOARDS, 6),                 \
		(5,     $ID_OVERLOARDS, 7),                 \
		(6,     5,              3),                 \
		(7,     5,              6),                 \
		(8,     6,              5);"

# Conversation 1: 1-2
# Conversation 2: 1-3
# Conversation 3: Group 1-2-3 name "barely a tournament chat" (not editable)
# Conversation 4: Group 1-2-3-4-5 name "barely ascrum room"
TABLE_NAME="barelyaschema.conversation"
insert_dummy "$TABLE_NAME"                                                                  \
	"INSERT INTO $TABLE_NAME                                                                \
        (id,    name,                       is_group_conversation,  is_editable) VALUES     \
		(1,     NULL,                       FALSE,                  TRUE),                  \
		(2,     NULL,                       FALSE,                  TRUE),                  \
		(3,     'barely a tournament chat', TRUE,                   FALSE),                 \
		(4,     'barely a scrum room',      TRUE,                   TRUE);"

TABLE_NAME="barelyaschema.conversation_member"
insert_dummy "$TABLE_NAME" \
	"INSERT INTO $TABLE_NAME \
        (id,    user_id,        conversation_id,    unread_counter) VALUES  \
		(1,     $ID_OVERLOARDS, 1,                  0),                     \
		(2,     $ID_OVERLOARDS, 2,                  0),                     \
		(3,     $ID_OVERLOARDS, 3,                  0),                     \
		(4,     $ID_OVERLOARDS, 4,                  0),                     \
		(5,     3,              1,                  0),                     \
		(6,     4,              1,                  1),                     \
		(7,     3,              2,                  0),                     \
		(8,     5,              2,                  1),                     \
		(9,     3,              3,                  0),                     \
		(10,    4,              3,                  3),                     \
		(11,    5,              3,                  3),                     \
		(12,    3,              4,                  0),                     \
		(13,    4,              4,                  0),                     \
		(14,    5,              4,                  0),                     \
		(15,    6,              4,                  0),                     \
		(16,    7,              4,                  0);"

TABLE_NAME="barelyaschema.message"
insert_dummy "$TABLE_NAME" \
	"INSERT INTO $TABLE_NAME \
        (id,    user_id,    conversation_id, created_at,                seen_at,                    content) VALUES                                     \
		(1,     3,          1,               '2024-01-01 10:42:00+00',  '2024-01-01 10:42:00+00',   'Hi Alex, how are you?'),                           \
		(2,     4,          1,               '2024-01-01 10:42:01+00',  '2024-01-01 10:42:01+00',   'Hi Alê, I am fine, thank you. How are you?'),      \
		(3,     3,          1,               '2024-01-01 10:42:02+00',   NULL,                      'I am fine too, thank you.'),                       \
		(4,     3,          2,               '2024-01-01 10:42:03+00',  '2024-01-01 10:42:03+00',   'Hi Anatolii, how are you?'),                       \
		(5,     5,          2,               '2024-01-01 10:42:04+00',  '2024-01-01 10:42:04+00',   'Hi Alê, I am fine, thank you. How are you?'),      \
		(6,     3,          2,               '2024-01-01 10:42:05+00',   NULL,                      'I am fine too, thank you.'),                       \
		(7,     3,          3,               '2024-01-01 10:42:06+00',   NULL,                      'Lets play this tournament'),                       \
		(8,     3,          3,               '2024-01-01 10:45:06+00',   NULL,                      'Someone in this conversation???'),                 \
		(9,     3,          3,               '2024-01-01 10:55:06+00',   NULL,                      'Booooriiiiinnggg!!!'),                             \
		(10,    4,          4,               '2024-01-01 10:42:06+00',   NULL,                      'This is the scrum roooooom!! Are u guys here?'),   \
		(11,    3,          4,               '2024-01-01 10:43:06+00',   NULL,                      'Hello :)'),                                        \
		(12,    5,          4,               '2024-01-01 10:44:06+00',   NULL,                      'Yes, I am here'),                                  \
		(13,    6,          4,               '2024-01-01 10:44:10+00',   NULL,                      'I am here too'),                                   \
		(14,    4,          4,               '2024-01-01 10:50:06+00',   NULL,                      'Oye oye, what about u @rphuyal?'),                 \
		(15,    7,          4,               '2024-01-01 10:51:06+00',   NULL,                      'Me as well'),                                      \
		(16,    3,          4,               '2024-01-01 10:52:56+00',   NULL,                      'Ok lets do this!');"

print_header "RESETING SEQUENCES..."
for table in "${ALL_TABLES[@]}"; do
    reset_sequence "$table"
done

print_header "Running 'create_dummy.sh'... DONE!"

printf "\033[1m > Check the wiki for details about the inserted dummy data:\033[0m\n"
printf "\033[1m > https://github.com/rajh-phuyal/42Transcendence/wiki/Database\033[0m\n"
