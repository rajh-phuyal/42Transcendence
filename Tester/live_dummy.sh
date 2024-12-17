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

# Function to insert dummy data into a table
insert_dummy()
{
  local table_name=$1
  local sql_query=$2
  printf "\e[33mInserting dummy data into table '%s'...\e[0m\n" "$table_name"
  docker exec -it db psql -U "admin" -d barelyalivedb -c "$sql_query" \
  	|| err_msg "Failed to insert dummy data into table '$table_name'."
  printf "\e[32mInserted dummy data into table '%s':\e[0m\n" "$table_name"
  # TODO: this needs to come somehow from theenv file
  # docker exec -it db psql -U admin -d barelyalivedb -c "SELECT * FROM $table_name;"
}

# Function to reset the sequence of a table's primary key
reset_sequence()
{
  local table_name=$1
  local sequence_name="${table_name}_id_seq"
  docker exec -it db psql -U admin -d barelyalivedb -c "SELECT setval('$sequence_name', COALESCE((SELECT MAX(id) FROM $table_name), 1) + 1, false);" \
  	|| err_msg "Failed to reset sequence for table '$table_name'."
  #printf "\e[32mSequence for table '%s' reset to match the highest current ID...\e[0m\n" "$table_name"
}

#-------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------
print_header "Running 'live_dummy.sh'..."

# Some private games
TABLE_NAME="barelyaschema.game"
insert_dummy "$TABLE_NAME"                                                                                                                                                                                                                                                      \
    "INSERT INTO $TABLE_NAME                                                                                                                                                                                                                                                    \
        (id, state,        map_number, powerups, tournament_id, deadline, finish_time) VALUES                                                                                                                                                                                   \
        (1, 'finished',     1,         TRUE,     NULL,         NULL,     '2024-01-10 12:15:30+00'),                                                                                                                                                                             \
        (2, 'finished',     2,         FALSE,    NULL,         NULL,     '2024-01-15 13:45:00+00'),                                                                                                                                                                             \
        (3, 'finished',     3,         TRUE,     NULL,         NULL,     '2024-01-20 14:00:00+00'),                                                                                                                                                                             \
        (4, 'quited',       4,         TRUE,     NULL,         NULL,     '2024-01-20 14:15:00+00'),                                                                                                                                                                                                 \
        (5, 'finished',     1,         FALSE,    NULL,         NULL,     '2024-02-01 15:25:00+00'),                                                                                                                                                                             \
        (6, 'finished',     2,         TRUE,     NULL,         NULL,     '2024-02-10 16:30:00+00'),                                                                                                                                                                             \
        (7, 'finished',     3,         FALSE,    NULL,         NULL,     '2024-02-15 10:45:00+00'),                                                                                                                                                                             \
        (8, 'finished',     4,         TRUE,     NULL,         NULL,     '2024-02-20 11:15:00+00'),                                                                                                                                                                             \
        (9, 'finished',     1,         FALSE,    NULL,         NULL,     '2024-03-01 12:00:00+00'),                                                                                                                                                                             \
        (10, 'finished',    2,         TRUE,     NULL,         NULL,     '2024-03-10 13:30:00+00'),                                                                                                                                                                             \
        (11, 'finished',    3,         FALSE,    NULL,         NULL,     '2024-03-15 14:15:00+00'),                                                                                                                                                                             \
        (12, 'finished',    4,         TRUE,     NULL,         NULL,     '2024-03-20 15:00:00+00'),                                                                                                                                                                             \
        (13, 'finished',    1,         FALSE,    NULL,         NULL,     '2024-04-01 16:30:00+00'),                                                                                                                                                                             \
        (14, 'finished',    2,         TRUE,     NULL,         NULL,     '2024-04-10 17:45:00+00'),                                                                                                                                                                             \
        (15, 'finished',    3,         FALSE,    NULL,         NULL,     '2024-04-15 18:00:00+00'),                                                                                                                                                                             \
        (16, 'finished',    4,         TRUE,     NULL,         NULL,     '2024-04-20 19:15:00+00'),                                                                                                                                                                             \
        (17, 'finished',    1,         TRUE,     NULL,         NULL,     '2024-05-01 20:30:00+00'),                                                                                                                                                                             \
        (18, 'finished',    2,         FALSE,    NULL,         NULL,     '2024-05-10 21:45:00+00'),                                                                                                                                                                             \
        (19, 'finished',    3,         TRUE,     NULL,         NULL,     '2024-05-15 22:15:00+00'),                                                                                                                                                                             \
        (20, 'finished',    4,         FALSE,    NULL,         NULL,     '2024-05-20 23:30:00+00'),                                                                                                                                                                             \
        (21, 'finished',    1,         TRUE,     NULL,         NULL,     '2024-06-01 10:00:00+00'),                                                                                                                                                                             \
        (22, 'finished',    2,         FALSE,    NULL,         NULL,     '2024-06-10 11:30:00+00'),                                                                                                                                                                             \
        (23, 'finished',    3,         TRUE,     NULL,         NULL,     '2024-06-15 12:45:00+00'),                                                                                                                                                                             \
        (24, 'finished',    4,         FALSE,    NULL,         NULL,     '2024-06-20 13:15:00+00'),                                                                                                                                                                             \
        (25, 'finished',    1,         TRUE,     NULL,         NULL,     '2024-07-01 14:30:00+00'),                                                                                                                                                                             \
        (26, 'finished',    2,         FALSE,    NULL,         NULL,     '2024-07-10 15:45:00+00'),                                                                                                                                                                             \
        (27, 'finished',    3,         TRUE,     NULL,         NULL,     '2024-07-15 16:15:00+00'),                                                                                                                                                                             \
        (28, 'finished',    4,         FALSE,    NULL,         NULL,     '2024-07-20 17:30:00+00'),                                                                                                                                                                             \
        (29, 'quited',      1,         TRUE,     NULL,         NULL,     '2024-07-20 17:31:00+00'),                                                                                                                                                                                                 \
        (30, 'quited',      2,         FALSE,    NULL,         NULL,     '2024-07-20 17:32:00+00'),                                                                                                                                                                                                 \
        (31, 'quited',      3,         TRUE,     NULL,         NULL,     '2024-07-20 17:33:00+00'),                                                                                                                                                                                                 \
        (32, 'quited',      4,         FALSE,    NULL,         NULL,     '2024-07-20 17:34:00+00'),                                                                                                                                                                                                 \
        (33, 'finished',    1,         TRUE,     NULL,         NULL,     '2024-08-01 18:30:00+00'),                                                                                                                                                                             \
        (34, 'finished',    2,         FALSE,    NULL,         NULL,     '2024-08-10 19:45:00+00'),                                                                                                                                                                             \
        (35, 'finished',    3,         TRUE,     NULL,         NULL,     '2024-08-15 20:15:00+00'),                                                                                                                                                                             \
        (36, 'finished',    4,         FALSE,    NULL,         NULL,     '2024-08-20 21:30:00+00'),                                                                                                                                                                             \
        (37, 'finished',    1,         TRUE,     NULL,         NULL,     '2024-09-01 22:45:00+00'),                                                                                                                                                                             \
        (38, 'pending',     2,         FALSE,    NULL,         NULL,     NULL),                                                                                                                                                                                                 \
        (39, 'ongoing',     3,         TRUE,     NULL,         NULL,     NULL),                                                                                                                                                                                                 \
        (40, 'paused',      4,         FALSE,    NULL,         NULL,     NULL);"

# And the member entrys for the games
TABLE_NAME="barelyaschema.game_member"
insert_dummy "$TABLE_NAME" \
    "INSERT INTO $TABLE_NAME \
        (id, user_id, game_id, local_game, points, result, powerup_big, powerup_fast, powerup_slow) VALUES \
        (1,       8,  1,  FALSE, 17, 'won',  FALSE, FALSE, FALSE), \
        (2,       9,  1,  FALSE, 15, 'lost', FALSE, FALSE, FALSE), \
        (3,      10,  2,  FALSE, 11, 'won',  FALSE, FALSE, FALSE), \
        (4,      11,  2,  FALSE,  7, 'lost', FALSE, FALSE, FALSE), \
        (5,      12,  3,  TRUE,   9, 'won',  FALSE, FALSE, FALSE), \
        (6,      13,  3,  FALSE,  5, 'lost', FALSE, FALSE, FALSE), \
        (7,       8,  4,  FALSE,  5, 'won',  FALSE, FALSE, FALSE), \
        (8,       9,  4,  FALSE,  7, 'lost', FALSE, FALSE, FALSE), \
        (9,      10,  5,  FALSE, 11, 'won',  FALSE, FALSE, FALSE), \
        (10,     11,  5,  TRUE,   8, 'lost', FALSE, FALSE, FALSE), \
        (11,     12,  6,  FALSE, 17, 'won',  FALSE, FALSE, FALSE), \
        (12,     13,  6,  FALSE, 15, 'lost', FALSE, FALSE, FALSE), \
        (13,      8,  7,  FALSE,  8, 'won',  FALSE, FALSE, FALSE), \
        (14,      9,  7,  FALSE,  6, 'lost', FALSE, FALSE, FALSE), \
        (15,     10,  8,  TRUE,  11, 'won',  FALSE, FALSE, FALSE), \
        (16,     11,  8,  FALSE,  7, 'lost', FALSE, FALSE, FALSE), \
        (17,     12,  9,  FALSE, 17, 'won',  FALSE, FALSE, FALSE), \
        (18,     13,  9,  FALSE, 15, 'lost', FALSE, FALSE, FALSE), \
        (19,      8, 10,  FALSE,  6, 'won',  FALSE, FALSE, FALSE), \
        (20,      9, 10,  FALSE,  5, 'lost', FALSE, FALSE, FALSE), \
        (21,     10, 11,  TRUE,   8, 'won',  FALSE, FALSE, FALSE), \
        (22,     11, 11,  FALSE,  7, 'lost', FALSE, FALSE, FALSE), \
        (23,     12, 12,  FALSE, 11, 'won',  FALSE, FALSE, FALSE), \
        (24,     13, 12,  FALSE,  9, 'lost', FALSE, FALSE, FALSE), \
        (25,      8, 13,  FALSE,  8, 'won',  FALSE, FALSE, FALSE), \
        (26,      9, 13,  TRUE,   6, 'lost', FALSE, FALSE, FALSE), \
        (27,     10, 14,  FALSE, 17, 'won',  FALSE, FALSE, FALSE), \
        (28,     11, 14,  FALSE, 15, 'lost', FALSE, FALSE, FALSE), \
        (29,     12, 15,  TRUE,   8, 'won',  FALSE, FALSE, FALSE), \
        (30,     13, 15,  FALSE,  7, 'lost', FALSE, FALSE, FALSE), \
        (31,      8, 16,  FALSE, 12, 'won',  FALSE, FALSE, FALSE), \
        (32,      9, 16,  TRUE,   9, 'lost', FALSE, FALSE, FALSE), \
        (33,     10, 17,  FALSE,  6, 'won',  FALSE, FALSE, FALSE), \
        (34,     11, 17,  FALSE,  5, 'lost', FALSE, FALSE, FALSE), \
        (35,     12, 18,  FALSE, 17, 'won',  FALSE, FALSE, FALSE), \
        (36,     13, 18,  FALSE, 15, 'lost', FALSE, FALSE, FALSE), \
        (37,      8, 19,  FALSE,  7, 'won',  FALSE, FALSE, FALSE), \
        (38,      9, 19,  TRUE,   5, 'lost', FALSE, FALSE, FALSE), \
        (39,     10, 20,  FALSE, 11, 'won',  FALSE, FALSE, FALSE), \
        (40,     11, 20,  FALSE,  9, 'lost', FALSE, FALSE, FALSE), \
        (41,     12, 21,  TRUE,  17, 'won',  FALSE, FALSE, FALSE), \
        (42,     13, 21,  FALSE, 15, 'lost', FALSE, FALSE, FALSE), \
        (43,      8, 22,  FALSE, 11, 'won',  FALSE, FALSE, FALSE), \
        (44,      9, 22,  TRUE,   9, 'lost', FALSE, FALSE, FALSE), \
        (45,     10, 23,  FALSE,  6, 'won',  FALSE, FALSE, FALSE), \
        (46,     11, 23,  FALSE,  5, 'lost', FALSE, FALSE, FALSE), \
        (47,     12, 24,  FALSE,  8, 'won',  FALSE, FALSE, FALSE), \
        (48,     13, 24,  FALSE,  6, 'lost', FALSE, FALSE, FALSE), \
        (49,      8, 25,  TRUE,  12, 'won',  FALSE, FALSE, FALSE), \
        (50,      9, 25,  FALSE,  9, 'lost', FALSE, FALSE, FALSE), \
        (51,     10, 26,  FALSE, 17, 'won',  FALSE, FALSE, FALSE), \
        (52,     11, 26,  FALSE, 15, 'lost', FALSE, FALSE, FALSE), \
        (53,     12, 27,  FALSE,  8, 'won',  FALSE, FALSE, FALSE), \
        (54,     13, 27,  TRUE,   7, 'lost', FALSE, FALSE, FALSE), \
        (55,      8, 28,  FALSE, 11, 'won',  FALSE, FALSE, FALSE), \
        (56,      9, 28,  FALSE,  9, 'lost', FALSE, FALSE, FALSE), \
        (57,     10, 29,  FALSE,  7, 'won',  FALSE, FALSE, FALSE), \
        (58,     11, 29,  TRUE,   5, 'lost', FALSE, FALSE, FALSE), \
        (59,     12, 30,  FALSE,  5, 'won',  FALSE, FALSE, FALSE), \
        (60,     13, 30,  FALSE,  2, 'lost', FALSE, FALSE, FALSE), \
        (61,     10, 31,  TRUE,   8, 'won',  FALSE, FALSE, FALSE), \
        (62,     11, 31,  FALSE,  7, 'lost', FALSE, FALSE, FALSE), \
        (63,     12, 32,  FALSE,  0, 'won',  FALSE, FALSE, FALSE), \
        (64,     13, 32,  FALSE,  0, 'lost', FALSE, FALSE, FALSE), \
        (65,      8, 33,  FALSE,  6, 'won',  FALSE, FALSE, FALSE), \
        (66,      9, 33,  FALSE,  5, 'lost', FALSE, FALSE, FALSE), \
        (67,     10, 34,  TRUE,   8, 'won',  FALSE, FALSE, FALSE), \
        (68,     11, 34,  FALSE,  7, 'lost', FALSE, FALSE, FALSE), \
        (69,     12, 35,  FALSE, 11, 'won',  FALSE, FALSE, FALSE), \
        (70,     13, 35,  FALSE,  9, 'lost', FALSE, FALSE, FALSE), \
        (71,      8, 36,  FALSE,  8, 'won',  FALSE, FALSE, FALSE), \
        (72,      9, 36,  TRUE,   6, 'lost', FALSE, FALSE, FALSE), \
        (73,     10, 37,  FALSE, 17, 'won',  FALSE, FALSE, FALSE), \
        (74,     11, 37,  FALSE, 15, 'lost', FALSE, FALSE, FALSE), \
        (75,      8, 38,  TRUE,   8, 'won',  FALSE, FALSE, FALSE), \
        (76,      9, 38,  FALSE,  6, 'lost', FALSE, FALSE, FALSE), \
        (77,     10, 39,  FALSE,  7, 'won',  FALSE, FALSE, FALSE), \
        (78,     11, 39,  TRUE,   5, 'lost', FALSE, FALSE, FALSE), \
        (79,     12, 40,  FALSE, 17, 'won',  FALSE, FALSE, FALSE), \
        (80,     13, 40,  FALSE, 15, 'lost', FALSE, FALSE, FALSE);"


print_header "RESETING SEQUENCES..."
for table in "${ALL_TABLES[@]}"; do
    reset_sequence "$table"
done