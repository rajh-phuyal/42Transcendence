#!/bin/bash
# ------------------------------------------------------------------------------
# ADD ALL TABLES INTO THIS ARRAY!
# (start from weak entity too not to break FK constraints)
# ------------------------------------------------------------------------------
ALL_TABLES=("barelyaschema.game_member"
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
ID_FLATMATE=3

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
insert_dummy "$TABLE_NAME"                                                                                                                                                                                                                                                      \
	"INSERT INTO $TABLE_NAME                                                                                                                                                                                                                                                    \
        (id,    password,               last_login,                 is_superuser,   username,          first_name,     last_name,  email,                  is_staff,   is_active,  date_joined,                avatar,                                      language) VALUES   \
        (4,     'hashed_password_1',    '2024-01-01 10:42:00+00',   FALSE,          's-ara',           'Alê',          'Guedes',   'we dont use email',    FALSE,      FALSE,      '2001-09-01 10:15:30+00',   '4d39f530-68c8-42eb-ad28-45445424da5b.png',  'pt-BR'  ),         \
        (5,     'hashed_password_2',    '2024-02-01 11:42:01+00',   FALSE,          's-ast',           'Alex',         'Stein',    'we dont use email',    FALSE,      FALSE,      '2002-09-01 10:15:30+00',   '73d3a3c0-f3ef-43a1-bdce-d798cb286f27.png',  'de-DE'  ),         \
        (6,     'hashed_password_3',    '2024-03-01 12:42:02+00',   FALSE,          's-ans',           'Anatolii',     'Shovah',   'we dont use email',    FALSE,      FALSE,      '2003-09-01 10:15:30+00',   '1e3751c5-5e47-45f2-9967-111fd26a6be8.png',  'uk-UA'  ),         \
        (7,     'hashed_password_4',    '2024-04-01 13:42:03+00',   FALSE,          's-fda',           'Francisco',    'Inácio',   'we dont use email',    FALSE,      FALSE,      '2004-09-01 10:15:30+00',   'fe468ade-12ed-4045-80a7-7d3e45be997e.png',  'pt-PT'  ),         \
        (8,     'hashed_password_5',    '2024-05-01 14:42:04+00',   FALSE,          's-rph',           'Rajh',         'Phuyal',   'we dont use email',    FALSE,      FALSE,      '2005-09-01 10:15:30+00',   'dd6e8101-fde8-469a-97dc-6b8bb9e8296e.png',  'ne-NP'  );"

TABLE_NAME="barelyaschema.is_cool_with"
insert_dummy "$TABLE_NAME"                                      \
	"INSERT INTO $TABLE_NAME                                    \
        (id,    requester_id,   requestee_id, status) VALUES    \
		(1,     $ID_AI,         4,          'accepted'),        \
		(2,     $ID_AI,         5,          'accepted'),        \
		(3,     $ID_AI,         6,          'accepted'),        \
		(4,     $ID_AI,         7,          'accepted'),        \
		(5,     $ID_AI,         8,          'accepted'),        \
        (6,     $ID_FLATMATE,   4,          'accepted'),        \
        (7,     $ID_FLATMATE,   5,          'accepted'),        \
        (8,     $ID_FLATMATE,   6,          'accepted'),        \
        (9,     $ID_FLATMATE,   7,          'accepted'),        \
        (10,    $ID_FLATMATE,   8,          'accepted'),        \
		(11,    4,              5,          'accepted'),        \
		(12,    4,              6,          'accepted'),        \
		(13,    4,              7,          'accepted'),        \
		(14,    4,              8,          'accepted'),        \
		(15,    5,              5,          'accepted'),        \
		(16,    5,              7,          'pending'),         \
		(17,    8,              7,          'pending');"

TABLE_NAME="barelyaschema.no_cool_with"
insert_dummy "$TABLE_NAME"                          \
	"INSERT INTO $TABLE_NAME                        \
        (id,    blocker_id,     blocked_id) VALUES  \
		(1,     $ID_OVERLOARDS, 4),                 \
		(2,     $ID_OVERLOARDS, 5),                 \
		(3,     $ID_OVERLOARDS, 6),                 \
		(4,     $ID_OVERLOARDS, 7),                 \
		(5,     $ID_OVERLOARDS, 8),                 \
		(6,     6,              4),                 \
		(7,     6,              7),                 \
		(8,     7,              6);"

# Conversation 1: 4-5
# Conversation 2: 4-6
TABLE_NAME="barelyaschema.conversation"
insert_dummy "$TABLE_NAME"                                                                  \
	"INSERT INTO $TABLE_NAME                                                                \
        (id,    name,                       is_group_conversation,  is_editable) VALUES     \
		(1,     NULL,                       FALSE,                  TRUE),                  \
		(2,     NULL,                       FALSE,                  TRUE);"

TABLE_NAME="barelyaschema.conversation_member"
insert_dummy "$TABLE_NAME" \
	"INSERT INTO $TABLE_NAME \
        (id,    user_id,        conversation_id,    unread_counter) VALUES  \
		(1,     4,              1,                  0),                     \
		(2,     5,              1,                  1),                     \
		(3,     4,              2,                  0),                     \
		(4,     6,              2,                  1);"

TABLE_NAME="barelyaschema.message"
insert_dummy "$TABLE_NAME" \
	"INSERT INTO $TABLE_NAME \
        (id,    user_id,                conversation_id, created_at,                seen_at,                    content) VALUES                                     \
		(1,     $ID_OVERLOARDS,         1,               '2024-01-01 10:42:00+00',  '2024-01-01 10:42:00+00',   '**S,4,6**'),                                       \
		(2,     4,                      1,               '2024-01-01 10:42:00+00',  '2024-01-01 10:42:00+00',   'Hi Alex, how are you?'),                           \
		(3,     5,                      1,               '2024-01-01 10:42:01+00',  '2024-01-01 10:42:01+00',   'Hi Alê, I am fine, thank you. How are you?'),      \
		(4,     4,                      1,               '2024-01-01 10:42:02+00',   NULL,                      'I am fine too, thank you.'),                       \
		(5,     $ID_OVERLOARDS,         2,               '2024-01-01 10:42:00+00',  '2024-01-01 10:42:00+00',   '**S,4,6**'),                                       \
		(6,     4,                      2,               '2024-01-01 10:42:03+00',  '2024-01-01 10:42:03+00',   'Hi Anatolii, how are you?'),                       \
		(7,     6,                      2,               '2024-01-01 10:42:04+00',  '2024-01-01 10:42:04+00',   'Hi Alê, I am fine, thank you. How are you?'),      \
		(8,     4,                      2,               '2024-01-01 10:42:05+00',   NULL,                      'I am fine too, thank you.');"

print_header "RESETING SEQUENCES..."
for table in "${ALL_TABLES[@]}"; do
    reset_sequence "$table"
done

print_header "Running 'create_dummy.sh'... DONE!"

printf "\033[1m > Check the wiki for details about the inserted dummy data:\033[0m\n"
printf "\033[1m > https://github.com/rajh-phuyal/42Transcendence/wiki/Database\033[0m\n"
