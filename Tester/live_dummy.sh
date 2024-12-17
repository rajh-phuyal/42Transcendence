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
  #printf "\e[33mInserting dummy data into table '%s'...\e[0m\n" "$table_name"
  docker exec -it db psql -U "admin" -d barelyalivedb -c "$sql_query" > /dev/null \
  	|| err_msg "Failed to insert dummy data into table '$table_name'."
  #printf "\e[32mInserted dummy data into table '%s':\e[0m\n" "$table_name"
  # TODO: this needs to come somehow from theenv file
  # docker exec -it db psql -U admin -d barelyalivedb -c "SELECT * FROM $table_name;"
}

# Function to reset the sequence of a table's primary key
reset_sequence()
{
  local table_name=$1
  local sequence_name="${table_name}_id_seq"
  docker exec -it db psql -U admin -d barelyalivedb -c "SELECT setval('$sequence_name', COALESCE((SELECT MAX(id) FROM $table_name), 1) + 1, false);" > /dev/null \
  	|| err_msg "Failed to reset sequence for table '$table_name'."
  #printf "\e[32mSequence for table '%s' reset to match the highest current ID...\e[0m\n" "$table_name"
}

#-------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------
print_header "Running 'live_dummy.sh'..."

# Some private games
echo "Creating some private games..."
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
echo "Creating game members for the private games..."
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

# Creating 10 dummy chats
echo "Creating 4 dummy conversations..."
TABLE_NAME="barelyaschema.conversation"
insert_dummy "$TABLE_NAME" \
    "INSERT INTO $TABLE_NAME \
        (id, name, is_group_conversation, is_editable) VALUES \
        (7,  NULL, FALSE, FALSE), \
        (8,  NULL, FALSE, FALSE), \
        (9,  NULL, FALSE, FALSE), \
        (10, NULL, FALSE, FALSE);"

echo "Creating conversation members for the dummy conversations..."
TABLE_NAME="barelyaschema.conversation_member"
insert_dummy "$TABLE_NAME" \
	"INSERT INTO $TABLE_NAME \
        (id,    user_id,        conversation_id,    unread_counter) VALUES  \
		(23,     $ID_OVERLOARDS, 7,                  0),                     \
		(24,     $ID_OVERLOARDS, 8,                  0),                     \
		(25,     $ID_OVERLOARDS, 9,                  0),                     \
		(26,     $ID_OVERLOARDS, 10,                 0),                     \
		(27,     3,              7,                  0),                     \
		(28,     8,              7,                  0),                     \
		(29,     4,              8,                  0),                     \
		(30,     9,              8,                  0),                     \
		(31,     5,              9,                  0),                     \
		(32,     10,             9,                  0),                     \
		(33,     6,              10,                 0),                     \
		(34,     11,             10,                 0);"

# Conversation 7: Restaurant Visit (100 messages)
# Conversation 8: Hello Exchange
# Conversation 9: 10 Messages of 'oye' from user 5
# Conversation 10: Coding School 42 (3 messages)
echo "Creating tons of messages for the conversations..."
TABLE_NAME="barelyaschema.message"
insert_dummy "$TABLE_NAME"                                                                                          \
    "INSERT INTO $TABLE_NAME                                                                                        \
        (id, user_id, conversation_id, created_at, seen_at, content) VALUES                                         \
        (50, 3, 7, '2024-01-01 10:00:00+00', '2024-01-01 10:20:00+00', 'Hey, where should we eat?'), \
        (51, 8, 7, '2024-01-01 10:01:00+00', '2024-01-01 10:25:00+00', 'How about Italian?'), \
        (52, 3, 7, '2024-01-01 10:05:00+00', '2024-01-01 10:30:00+00', 'Sure, sounds great!'), \
        (53, 8, 7, '2024-01-01 10:10:00+00', '2024-01-01 10:35:00+00', 'What time works for you?'), \
        (54, 3, 7, '2024-01-01 10:15:00+00', '2024-01-01 10:45:00+00', 'Tonight at 7?'), \
        (55, 8, 7, '2024-01-01 10:20:00+00', '2024-01-01 10:55:00+00', 'Perfect, see you then!'), \
        (56, 3, 7, '2024-01-01 11:00:00+00', '2024-01-01 11:30:00+00', 'I’ll book a table.'), \
        (57, 8, 7, '2024-01-01 11:05:00+00', '2024-01-01 11:40:00+00', 'Thanks!'), \
        (58, 3, 7, '2024-01-01 12:00:00+00', '2024-01-01 12:40:00+00', 'Do you want starters?'), \
        (59, 8, 7, '2024-01-01 12:10:00+00', '2024-01-01 12:50:00+00', 'Yes, garlic bread!'), \
        (60, 3, 7, '2024-01-01 13:00:00+00', '2024-01-01 13:40:00+00', 'Same here!'), \
        (61, 8, 7, '2024-01-01 13:05:00+00', '2024-01-01 13:50:00+00', 'See you soon.'), \
        (62, 3, 7, '2024-01-01 14:00:00+00', '2024-01-01 14:40:00+00', 'Looking forward to it.'), \
        (63, 8, 7, '2024-01-01 14:10:00+00', '2024-01-01 14:50:00+00', 'What’s the dress code?'), \
        (64, 3, 7, '2024-01-01 15:00:00+00', '2024-01-01 15:40:00+00', 'Casual is fine.'), \
        (65, 8, 7, '2024-01-01 15:10:00+00', '2024-01-01 15:50:00+00', 'Okay, cool!'), \
        (66, 3, 7, '2024-01-01 16:00:00+00', '2024-01-01 16:40:00+00', 'Booked!'), \
        (67, 8, 7, '2024-01-01 16:10:00+00', '2024-01-01 16:50:00+00', 'You’re awesome!'), \
        (68, 3, 7, '2024-01-01 17:00:00+00', '2024-01-01 17:40:00+00', 'See you soon.'), \
        (69, 8, 7, '2024-01-01 17:10:00+00', '2024-01-01 17:50:00+00', 'Bye!'), \
        (70, 3, 7, '2024-01-02 10:00:00+00', '2024-01-02 10:30:00+00', 'I’m on my way.'), \
        (71, 8, 7, '2024-01-02 10:05:00+00', '2024-01-02 10:40:00+00', 'Me too!'), \
        (72, 3, 7, '2024-01-02 11:00:00+00', '2024-01-02 11:30:00+00', 'I’m on my way!'), \
        (73, 8, 7, '2024-01-02 11:05:00+00', '2024-01-02 11:45:00+00', 'Me too, see you soon!'), \
        (74, 3, 7, '2024-01-02 12:00:00+00', '2024-01-02 12:40:00+00', 'Did you find parking?'), \
        (75, 8, 7, '2024-01-02 12:10:00+00', '2024-01-02 12:50:00+00', 'Yeah, a bit crowded though.'), \
        (76, 3, 7, '2024-01-02 12:20:00+00', '2024-01-02 13:00:00+00', 'I’m inside already.'), \
        (77, 8, 7, '2024-01-02 12:25:00+00', '2024-01-02 13:05:00+00', 'Ordering drinks, want anything?'), \
        (78, 3, 7, '2024-01-02 12:30:00+00', '2024-01-02 13:10:00+00', 'Just water for now.'), \
        (79, 8, 7, '2024-01-02 12:35:00+00', '2024-01-02 13:15:00+00', 'Got it, see you in a sec!'), \
        (80, 3, 7, '2024-01-02 12:45:00+00', '2024-01-02 13:25:00+00', 'What are you thinking of eating?'), \
        (81, 8, 7, '2024-01-02 12:50:00+00', '2024-01-02 13:30:00+00', 'The lasagna sounds good.'), \
        (82, 3, 7, '2024-01-02 13:00:00+00', '2024-01-02 13:40:00+00', 'I might go for the pizza.'), \
        (83, 8, 7, '2024-01-02 13:05:00+00', '2024-01-02 13:45:00+00', 'Nice choice!'), \
        (84, 3, 7, '2024-01-02 13:10:00+00', '2024-01-02 13:50:00+00', 'Do we want dessert?'), \
        (85, 8, 7, '2024-01-02 13:15:00+00', '2024-01-02 13:55:00+00', 'Tiramisu maybe?'), \
        (86, 3, 7, '2024-01-02 13:20:00+00', '2024-01-02 14:00:00+00', 'Sounds perfect!'), \
        (87, 8, 7, '2024-01-02 13:25:00+00', '2024-01-02 14:05:00+00', 'Great dinner, thanks for joining!'), \
        (88, 3, 7, '2024-01-02 13:30:00+00', '2024-01-02 14:10:00+00', 'Always a pleasure.'), \
        (89, 8, 7, '2024-01-02 13:35:00+00', '2024-01-02 14:15:00+00', 'We should do this again soon.'), \
        (90, 3, 7, '2024-01-02 13:40:00+00', '2024-01-02 14:20:00+00', 'Agreed, let’s pick a date!'), \
        (91, 8, 7, '2024-01-02 13:45:00+00', '2024-01-02 14:25:00+00', 'How about next week?'), \
        (92, 3, 7, '2024-01-02 13:50:00+00', '2024-01-02 14:30:00+00', 'Works for me!'), \
        (93, 8, 7, '2024-01-02 14:00:00+00', '2024-01-02 14:40:00+00', 'See you then!'), \
        (94, 3, 7, '2024-01-02 14:05:00+00', '2024-01-02 14:45:00+00', 'See you!'), \
        (95, 8, 7, '2024-01-02 15:00:00+00', '2024-01-02 15:40:00+00', 'Take care!'), \
        (96, 3, 7, '2024-01-02 15:05:00+00', '2024-01-02 15:45:00+00', 'You too!'), \
        (97, 8, 7, '2024-01-02 15:10:00+00', '2024-01-02 15:50:00+00', 'Bye!'), \
        (98, 3, 7, '2024-01-02 15:15:00+00', '2024-01-02 15:55:00+00', 'Bye!'), \
        (99, 8, 7, '2024-01-02 15:20:00+00', '2024-01-02 16:00:00+00', 'Talk soon.'), \
        (100, 3, 7, '2024-01-02 15:25:00+00', '2024-01-02 16:05:00+00', 'Absolutely!'), \
        (101, 8, 7, '2024-01-03 11:00:00+00', '2024-01-03 11:40:00+00', 'Hey, did you enjoy the food?'), \
        (102, 3, 7, '2024-01-03 11:05:00+00', '2024-01-03 11:45:00+00', 'Yes, it was amazing!'), \
        (103, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'Glad to hear that!'), \
        (104, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'Let’s go back soon.'), \
        (105, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'Lets play ping pong!'), \
        (106, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'Lets go: ping'), \
        (107, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        (108, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (109, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        (110, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (111, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        (112, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (113, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        (114, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (115, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        (116, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (117, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        (118, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (119, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        (120, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (121, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        (122, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (123, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        (124, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (125, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        (126, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (127, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        (128, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (129, 8, 7, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        (130, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (131, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (132, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (133, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (134, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (135, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (136, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (137, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (138, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (139, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (140, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (141, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (142, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (143, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (144, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (145, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (146, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (147, 3, 7, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        (148, 3, 7, '2024-01-05 10:00:00+00', '2024-01-05 10:40:00+00', 'Next time’s on me!'), \
        (149, 8, 7, '2024-01-05 10:05:00+00', '2024-01-05 10:45:00+00', 'Deal!'), \
        (150, 4, 8, '2024-02-01 12:00:00+00', '2024-02-01 12:20:00+00', 'Hello?'), \
        (151, 9, 8, '2024-02-01 12:01:00+00', '2024-02-01 12:30:00+00', 'Hello!'), \
        (152, 5, 9, '2024-02-01 13:00:00+00', '2024-02-01 13:20:00+00', 'Oye'), \
        (153, 5, 9, '2024-02-01 13:10:00+00', '2024-02-01 13:30:00+00', 'Oye'), \
        (154, 5, 9, '2024-02-01 13:20:00+00', '2024-02-01 13:50:00+00', 'Oye'), \
        (155, 5, 9, '2024-02-01 13:30:00+00', '2024-02-01 14:00:00+00', 'Oye'), \
        (156, 5, 9, '2024-02-01 13:40:00+00', '2024-02-01 14:10:00+00', 'Oye'), \
        (157, 5, 9, '2024-02-01 13:50:00+00', '2024-02-01 14:20:00+00', 'Oye'), \
        (158, 5, 9, '2024-02-01 14:00:00+00', '2024-02-01 14:30:00+00', 'Oye'), \
        (159, 5, 9, '2024-02-01 14:10:00+00', '2024-02-01 14:40:00+00', 'Oye'), \
        (160, 5, 9, '2024-02-01 14:20:00+00', '2024-02-01 14:50:00+00', 'Oye'), \
        (161, 5, 9, '2024-02-01 14:30:00+00', '2024-02-01 15:00:00+00', 'Oye'), \
        (162, 6, 10, '2024-03-01 10:00:00+00', '2024-03-01 10:30:00+00', 'Have you heard of 42?'), \
        (163, 11, 10, '2024-03-01 10:01:00+00', '2024-03-01 10:31:00+00', 'Yeah, it’s amazing!'), \
        (164, 11, 10, '2024-03-01 14:10:00+00', '2024-03-01 14:40:00+00', 'Let’s apply together!');"

# Creating finished tournament games
# 41-48: Tournament 1: Round Robin between players:8,9,10,11
# 49-75: Tournament 2: Round Robin between players:3-11
echo "Creating finished tournament games..."
echo -e "CREATING GAMES:\tTournament 1: Round Robin between players:8,9,10,11"
echo -e "CREATING GAMES:\tTournament 2: Round Robin between players:3,4,5,6,7,8,9,10,11"
TABLE_NAME="barelyaschema.game"
insert_dummy "$TABLE_NAME" \
    "INSERT INTO $TABLE_NAME \
        (id, state, map_number, powerups, tournament_id, deadline, finish_time) VALUES \
        -- Round Robin Matches (6 games)
        (41, 'finished', 2, TRUE, 1, '2024-07-01 13:29:00+00', '2024-07-01 13:30:00+00'), \
        (42, 'finished', 2, TRUE, 1, '2024-07-01 14:29:00+00', '2024-07-01 14:30:00+00'), \
        (43, 'finished', 2, TRUE, 1, '2024-07-01 15:29:00+00', '2024-07-01 15:30:00+00'), \
        (44, 'finished', 2, TRUE, 1, '2024-07-01 16:29:00+00', '2024-07-01 16:30:00+00'), \
        (45, 'finished', 2, TRUE, 1, '2024-07-01 17:29:00+00', '2024-07-01 17:30:00+00'), \
        (46, 'finished', 2, TRUE, 1, '2024-07-01 18:29:00+00', '2024-07-01 18:30:00+00'), \
        -- Semi-Finale (1 game)
        (47, 'finished', 2, TRUE, 1, '2024-07-01 19:29:00+00', '2024-07-01 19:30:00+00'), \
        -- Finale (1 game)
        (48, 'finished', 2, TRUE, 1, '2024-07-01 20:29:00+00', '2024-07-01 20:30:00+00'), \
        -- Tournament 2
        -- Round 1
        (49, 'finished', 4, FALSE, 2, '2024-08-01 07:59:00+00', '2024-08-01 08:00:00+00'), \
        (50, 'finished', 4, FALSE, 2, '2024-08-01 08:29:00+00', '2024-08-01 08:30:00+00'), \
        (51, 'finished', 4, FALSE, 2, '2024-08-01 08:59:00+00', '2024-08-01 09:00:00+00'), \
        (52, 'finished', 4, FALSE, 2, '2024-08-01 09:29:00+00', '2024-08-01 09:30:00+00'), \
        (53, 'finished', 4, FALSE, 2, '2024-08-01 09:59:00+00', '2024-08-01 10:00:00+00'), \
        (54, 'finished', 4, FALSE, 2, '2024-08-01 10:29:00+00', '2024-08-01 10:30:00+00'), \
        (55, 'finished', 4, FALSE, 2, '2024-08-01 10:59:00+00', '2024-08-01 11:00:00+00'), \
        (56, 'finished', 4, FALSE, 2, '2024-08-01 11:29:00+00', '2024-08-01 11:30:00+00'), \
        (57, 'finished', 4, FALSE, 2, '2024-08-01 11:59:00+00', '2024-08-01 12:00:00+00'), \
        (58, 'finished', 4, FALSE, 2, '2024-08-01 12:29:00+00', '2024-08-01 12:30:00+00'), \
        (59, 'finished', 4, FALSE, 2, '2024-08-01 12:59:00+00', '2024-08-01 13:00:00+00'), \
        (60, 'finished', 4, FALSE, 2, '2024-08-01 13:29:00+00', '2024-08-01 13:30:00+00'), \
        (61, 'finished', 4, FALSE, 2, '2024-08-01 13:59:00+00', '2024-08-01 14:00:00+00'), \
        (62, 'finished', 4, FALSE, 2, '2024-08-01 14:29:00+00', '2024-08-01 14:30:00+00'), \
        (63, 'finished', 4, FALSE, 2, '2024-08-01 14:59:00+00', '2024-08-01 15:00:00+00'), \
        (64, 'finished', 4, FALSE, 2, '2024-08-01 15:29:00+00', '2024-08-01 15:30:00+00'), \
        (65, 'finished', 4, FALSE, 2, '2024-08-01 15:59:00+00', '2024-08-01 16:00:00+00'), \
        (66, 'finished', 4, FALSE, 2, '2024-08-01 16:29:00+00', '2024-08-01 16:30:00+00'), \
        (67, 'finished', 4, FALSE, 2, '2024-08-01 16:59:00+00', '2024-08-01 17:00:00+00'), \
        (68, 'finished', 4, FALSE, 2, '2024-08-01 17:29:00+00', '2024-08-01 17:30:00+00'), \
        (69, 'finished', 4, FALSE, 2, '2024-08-01 17:59:00+00', '2024-08-01 18:00:00+00'), \
        (70, 'finished', 4, FALSE, 2, '2024-08-01 18:29:00+00', '2024-08-01 18:30:00+00'), \
        (71, 'finished', 4, FALSE, 2, '2024-08-01 18:59:00+00', '2024-08-01 19:00:00+00'), \
        (72, 'finished', 4, FALSE, 2, '2024-08-01 19:29:00+00', '2024-08-01 19:30:00+00'), \
        -- Semi-Finale 1
        (73, 'finished', 4, FALSE, 2, '2024-08-01 19:59:00+00', '2024-08-01 20:00:00+00'), \
        -- Semi-Finale 2
        (74, 'finished', 4, FALSE, 2, '2024-08-01 20:29:00+00', '2024-08-01 20:30:00+00'), \
        -- Finale
        (75, 'finished', 4, FALSE, 2, '2024-08-01 20:59:00+00', '2024-08-01 21:00:00+00');"

# Creating GameMembers for the tournament games
# 81-96: Tournament 1: Round Robin between players:8,9,10,11
echo -e "CREATING GAME MEMBERS\tTournament 1: Round Robin between players:8,9,10,11"
echo -e "CREATING GAME MEMBERS\tTournament 2: Round Robin between players:3,4,5,6,7,8,9,10,11"
TABLE_NAME="barelyaschema.game_member"
insert_dummy "$TABLE_NAME" \
    "INSERT INTO $TABLE_NAME \
        (id, user_id, game_id, local_game, points, result, powerup_big, powerup_fast, powerup_slow) VALUES \
        -- Game 41
        (81, 8, 41, FALSE, 11, 'won', TRUE, FALSE, FALSE), \
        (82, 9, 41, FALSE, 9,  'lost', FALSE, TRUE, FALSE), \
        -- Game 42
        (83, 8, 42, FALSE, 13, 'won', FALSE, FALSE, TRUE), \
        (84, 10, 42, FALSE, 11, 'lost', TRUE, TRUE, FALSE), \
        -- Game 43
        (85, 8, 43, FALSE, 11, 'won', FALSE, TRUE, FALSE), \
        (86, 11, 43, FALSE, 9,  'lost', TRUE, FALSE, TRUE), \
        -- Game 44
        (87, 9, 44, FALSE, 11, 'won', TRUE, FALSE, FALSE), \
        (88, 10, 44, FALSE, 8,  'lost', FALSE, TRUE, FALSE), \
        -- Game 45
        (89, 9, 45, FALSE, 13, 'won', FALSE, TRUE, FALSE), \
        (90, 11, 45, FALSE, 11, 'lost', TRUE, FALSE, TRUE), \
        -- Game 46
        (91, 10, 46, FALSE, 11, 'won', FALSE, FALSE, TRUE), \
        (92, 11, 46, FALSE, 9,  'lost', TRUE, TRUE, FALSE), \
        -- Semi-Finale (Game 47)
        (93, 9, 47, FALSE, 15, 'won', TRUE, FALSE, TRUE), \
        (94, 10, 47, FALSE, 13, 'lost', FALSE, TRUE, FALSE), \
        -- Finale (Game 48)
        (95, 8, 48, FALSE, 11, 'won', TRUE, TRUE, FALSE), \
        (96, 9, 48, FALSE, 9,  'lost', FALSE, FALSE, TRUE), \
        -- Tournament 2
        -- Round 1
        (97, 3, 49, FALSE, 11, 'won', FALSE, FALSE, FALSE), \
        (98, 4, 49, FALSE, 9, 'lost', FALSE, FALSE, FALSE), \
        (99, 5, 50, FALSE, 13, 'won', FALSE, FALSE, FALSE), \
        (100, 6, 50, FALSE, 11, 'lost', FALSE, FALSE, FALSE), \
        (101, 7, 51, FALSE, 11, 'won', FALSE, FALSE, FALSE), \
        (102, 8, 51, FALSE, 9, 'lost', FALSE, FALSE, FALSE), \
        (103, 9, 52, FALSE, 13, 'won', FALSE, FALSE, FALSE), \
        (104, 10, 52, FALSE, 11, 'lost', FALSE, FALSE, FALSE), \
        (105, 3, 53, FALSE, 11, 'won', FALSE, FALSE, FALSE), \
        (106, 5, 53, FALSE, 9, 'lost', FALSE, FALSE, FALSE), \
        (107, 6, 54, FALSE, 13, 'won', FALSE, FALSE, FALSE), \
        (108, 7, 54, FALSE, 11, 'lost', FALSE, FALSE, FALSE), \
        (109, 8, 55, FALSE, 11, 'won', FALSE, FALSE, FALSE), \
        (110, 9, 55, FALSE, 9, 'lost', FALSE, FALSE, FALSE), \
        (111, 10, 56, FALSE, 13, 'won', FALSE, FALSE, FALSE), \
        (112, 11, 56, FALSE, 11, 'lost', FALSE, FALSE, FALSE), \
        (113, 3, 57, FALSE, 11, 'won', FALSE, FALSE, FALSE), \
        (114, 6, 57, FALSE, 9, 'lost', FALSE, FALSE, FALSE), \
        (115, 7, 58, FALSE, 13, 'won', FALSE, FALSE, FALSE), \
        (116, 8, 58, FALSE, 11, 'lost', FALSE, FALSE, FALSE), \
        (117, 9, 59, FALSE, 11, 'won', FALSE, FALSE, FALSE), \
        (118, 10, 59, FALSE, 9, 'lost', FALSE, FALSE, FALSE), \
        (119, 4, 60, FALSE, 13, 'won', FALSE, FALSE, FALSE), \
        (120, 5, 60, FALSE, 11, 'lost', FALSE, FALSE, FALSE), \
        (121, 6, 61, FALSE, 11, 'won', FALSE, FALSE, FALSE), \
        (122, 7, 61, FALSE, 9, 'lost', FALSE, FALSE, FALSE), \
        (123, 8, 62, FALSE, 13, 'won', FALSE, FALSE, FALSE), \
        (124, 9, 62, FALSE, 11, 'lost', FALSE, FALSE, FALSE), \
        (125, 10, 63, FALSE, 11, 'won', FALSE, FALSE, FALSE), \
        (126, 11, 63, FALSE, 9, 'lost', FALSE, FALSE, FALSE), \
        (127, 3, 64, FALSE, 13, 'won', FALSE, FALSE, FALSE), \
        (128, 8, 64, FALSE, 11, 'lost', FALSE, FALSE, FALSE), \
        (129, 9, 65, FALSE, 11, 'won', FALSE, FALSE, FALSE), \
        (130, 4, 65, FALSE, 9, 'lost', FALSE, FALSE, FALSE), \
        (131, 5, 66, FALSE, 13, 'won', FALSE, FALSE, FALSE), \
        (132, 10, 66, FALSE, 11, 'lost', FALSE, FALSE, FALSE), \
        (133, 11, 67, FALSE, 11, 'won', FALSE, FALSE, FALSE), \
        (134, 6, 67, FALSE, 9, 'lost', FALSE, FALSE, FALSE), \
        (135, 7, 68, FALSE, 13, 'won', FALSE, FALSE, FALSE), \
        (136, 3, 68, FALSE, 11, 'lost', FALSE, FALSE, FALSE), \
        (137, 4, 69, FALSE, 11, 'won', FALSE, FALSE, FALSE), \
        (138, 5, 69, FALSE, 9, 'lost', FALSE, FALSE, FALSE), \
        (139, 6, 70, FALSE, 13, 'won', FALSE, FALSE, FALSE), \
        (140, 7, 70, FALSE, 11, 'lost', FALSE, FALSE, FALSE), \
        (141, 8, 71, FALSE, 11, 'won', FALSE, FALSE, FALSE), \
        (142, 9, 71, FALSE, 9, 'lost', FALSE, FALSE, FALSE), \
        (143, 10, 72, FALSE, 13, 'won', FALSE, FALSE, FALSE), \
        (144, 11, 72, FALSE, 11, 'lost', FALSE, FALSE, FALSE), \
        -- Semi-Finale 1
        (145, 3, 73, FALSE, 15, 'won', FALSE, FALSE, FALSE), \
        (146, 4, 73, FALSE, 13, 'lost', FALSE, FALSE, FALSE), \
        -- Semi-Finale 2
        (147, 5, 74, FALSE, 11, 'won', FALSE, FALSE, FALSE), \
        (148, 6, 74, FALSE, 9, 'lost', FALSE, FALSE, FALSE), \
        -- Finale
        (149, 3, 75, FALSE, 15, 'won', FALSE, FALSE, FALSE), \
        (150, 5, 75, FALSE, 13, 'lost', FALSE, FALSE, FALSE);"

# Create the actual tournament
echo -e "CREATING TOURNAMENTS:\tTournament 1: Round Robin between players:8,9,10,11"
echo -e "CREATING TOURNAMENTS:\tTournament 2: Round Robin between players:3,4,5,6,7,8,9,10,11"
echo -e "CREATING TOURNAMENTS:\tTournament 3: Round Robin Public in setup"
echo -e "CREATING TOURNAMENTS:\tTournament 4: Round Robin Private in setup"
TABLE_NAME="barelyaschema.tournament"
insert_dummy "$TABLE_NAME" \
    "INSERT INTO $TABLE_NAME \
        (id, state,     name,                                           local_tournament, public_tournament, map_number, powerups,  finish_time) VALUES        \
        (1, 'finished', 'Round Robin Tournament Players 8,9,10,11',     FALSE,            TRUE,              2,          TRUE,      '2024-07-01 20:30:00+00'), \
        (2, 'finished', 'Round Robin Tournament Players 3-11',          FALSE,            FALSE,             4,          FALSE,     '2024-08-01 21:00:00+00'), \
        (3, 'setup',    'Let’s play!?',                                 FALSE,            TRUE,              3,          TRUE,      NULL),                     \
        (4, 'setup',    'This is a private one ;)',                     FALSE,            FALSE ,            1,          TRUE,      NULL);"

# Create the tournament members
echo -e "CREATING TOURNAMENT MEMBERS:\tTournament 1: Round Robin between players:8,9,10,11"
echo -e "CREATING TOURNAMENT MEMBERS:\tTournament 2: Round Robin between players:3,4,5,6,7,8,9,10,11"
echo -e "CREATING TOURNAMENT MEMBERS:\tTournament 3: Round Robin Public in setup"
echo -e "CREATING TOURNAMENT MEMBERS:\tTournament 4: Round Robin Private in setup"
TABLE_NAME="barelyaschema.tournament_member"
insert_dummy "$TABLE_NAME" \
    "INSERT INTO $TABLE_NAME \
        (id, user_id, tournament_id, tournament_alias, is_admin, accepted, finish_place) VALUES \
        (1, 8, 1,   'Player 8',     TRUE,    TRUE, 1), \
        (2, 9, 1,   'Player 9',     FALSE,   TRUE, 2), \
        (3, 10, 1,  'Player 10',    FALSE,   TRUE, 3), \
        (4, 11, 1,  'Player 11',    FALSE,   TRUE, 4), \
        (5, 3, 2,   'Player 3',     TRUE,    TRUE, 1), \
        (6, 5, 2,   'Player 5',     FALSE,   TRUE, 2), \
        (7, 4, 2,   'Player 4',     FALSE,   TRUE, 3), \
        (8, 6, 2,   'Player 6',     FALSE,   TRUE, 4), \
        (9, 7, 2,   'Player 7',     FALSE,   TRUE, 5), \
        (10, 8, 2,  'Player 8',     FALSE,   TRUE, 6), \
        (11, 9, 2,  'Player 9',     FALSE,   TRUE, 7), \
        (12, 10, 2, 'Player 10',    FALSE,   TRUE, 8), \
        (13, 11, 2, 'Player 11',    FALSE,   TRUE, 9), \
        (14, 10, 3, 'Player 10',    TRUE,    TRUE, NULL), \
        (15, 11, 3, 'Player 11',    FALSE,   TRUE, NULL), \
        (16, 3, 4,  'Player 3',     TRUE,    TRUE, NULL), \
        (17, 4, 4,  'Player 4',     FALSE,   FALSE, NULL), \
        (18, 5, 4,  'Player 5',     FALSE,   TRUE, NULL);"

print_header "RESETING SEQUENCES..."
for table in "${ALL_TABLES[@]}"; do
    reset_sequence "$table"
done