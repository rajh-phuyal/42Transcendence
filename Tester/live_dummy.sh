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

# Function to insert dummy data into a table
insert_dummy()
{
  local table_name=$1
  local sql_query=$2
  #printf "\e[33mInserting dummy data into table '%s'...\e[0m\n" "$table_name"
  docker exec -it db psql -U "admin" -d barelyalivedb -c "$sql_query" > /dev/null \
  	|| err_msg "Failed to insert dummy data into table '$table_name'."
  #printf "\e[32mInserted dummy data into table '%s':\e[0m\n" "$table_name"
  # FUTURE: this needs to come somehow from theenv file
  #docker exec -it db psql -U admin -d barelyalivedb -c "SELECT * FROM $table_name;"
}

# Function to reset the sequence of a table's primary key
reset_sequence()
{
  local table_name=$1
  local sequence_name="${table_name}_id_seq"
  docker exec -it db psql -U admin -d barelyalivedb -c "SELECT setval('$sequence_name', COALESCE((SELECT MAX(id) FROM $table_name), 1) + 1, false);"
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
        (1,  'finished',    1,         TRUE,     NULL,         NULL,     '2024-01-10 12:15:30+00'),   \
        (2,  'finished',    2,         FALSE,    NULL,         NULL,     '2024-01-15 13:45:00+00'),   \
        (3,  'finished',    3,         TRUE,     NULL,         NULL,     '2024-01-20 14:00:00+00'),   \
        (4,  'quited',      4,         TRUE,     NULL,         NULL,     '2024-01-20 14:15:00+00'),   \
        (5,  'finished',    1,         FALSE,    NULL,         NULL,     '2024-02-01 15:25:00+00'),   \
        (6,  'finished',    2,         TRUE,     NULL,         NULL,     '2024-02-10 16:30:00+00'),   \
        (7,  'finished',    3,         FALSE,    NULL,         NULL,     '2024-02-15 10:45:00+00'),   \
        (8,  'finished',    4,         TRUE,     NULL,         NULL,     '2024-02-20 11:15:00+00'),   \
        (9,  'finished',    1,         FALSE,    NULL,         NULL,     '2024-03-01 12:00:00+00'),   \
        (10, 'finished',    2,         TRUE,     NULL,         NULL,     '2024-03-10 13:30:00+00'),   \
        (11, 'finished',    3,         FALSE,    NULL,         NULL,     '2024-03-15 14:15:00+00'),   \
        (12, 'finished',    4,         TRUE,     NULL,         NULL,     '2024-03-20 15:00:00+00'),   \
        (13, 'finished',    1,         FALSE,    NULL,         NULL,     '2024-04-01 16:30:00+00'),   \
        (14, 'finished',    2,         TRUE,     NULL,         NULL,     '2024-04-10 17:45:00+00'),   \
        (15, 'finished',    3,         FALSE,    NULL,         NULL,     '2024-04-15 18:00:00+00'),   \
        (16, 'finished',    4,         TRUE,     NULL,         NULL,     '2024-04-20 19:15:00+00'),   \
        (17, 'finished',    1,         TRUE,     NULL,         NULL,     '2024-05-01 20:30:00+00'),   \
        (18, 'finished',    2,         FALSE,    NULL,         NULL,     '2024-05-10 21:45:00+00'),   \
        (19, 'finished',    3,         TRUE,     NULL,         NULL,     '2024-05-15 22:15:00+00'),   \
        (20, 'finished',    4,         FALSE,    NULL,         NULL,     '2024-05-20 23:30:00+00'),   \
        (21, 'finished',    1,         TRUE,     NULL,         NULL,     '2024-06-01 10:00:00+00'),   \
        (22, 'finished',    2,         FALSE,    NULL,         NULL,     '2024-06-10 11:30:00+00'),   \
        (23, 'finished',    3,         TRUE,     NULL,         NULL,     '2024-06-15 12:45:00+00'),   \
        (24, 'finished',    4,         FALSE,    NULL,         NULL,     '2024-06-20 13:15:00+00'),   \
        (25, 'finished',    1,         TRUE,     NULL,         NULL,     '2024-07-01 14:30:00+00'),   \
        (26, 'finished',    2,         FALSE,    NULL,         NULL,     '2024-07-10 15:45:00+00'),   \
        (27, 'finished',    3,         TRUE,     NULL,         NULL,     '2024-07-15 16:15:00+00'),   \
        (28, 'finished',    4,         FALSE,    NULL,         NULL,     '2024-07-20 17:30:00+00'),   \
        (29, 'quited',      1,         TRUE,     NULL,         NULL,     '2024-07-20 17:31:00+00'),   \
        (30, 'quited',      2,         FALSE,    NULL,         NULL,     '2024-07-20 17:32:00+00'),   \
        (31, 'quited',      3,         TRUE,     NULL,         NULL,     '2024-07-20 17:33:00+00'),   \
        (32, 'quited',      4,         FALSE,    NULL,         NULL,     '2024-07-20 17:34:00+00'),   \
        (33, 'finished',    1,         TRUE,     NULL,         NULL,     '2024-08-01 18:30:00+00'),   \
        (34, 'finished',    2,         FALSE,    NULL,         NULL,     '2024-08-10 19:45:00+00'),   \
        (35, 'finished',    3,         TRUE,     NULL,         NULL,     '2024-08-15 20:15:00+00'),   \
        (36, 'finished',    4,         FALSE,    NULL,         NULL,     '2024-08-20 21:30:00+00'),   \
        (37, 'finished',    1,         TRUE,     NULL,         NULL,     '2024-09-01 22:45:00+00'),   \
        (38, 'pending',     2,         FALSE,    NULL,         NULL,     NULL),                       \
        (39, 'ongoing',     3,         TRUE,     NULL,         NULL,     NULL),                       \
        (40, 'paused',      4,         FALSE,    NULL,         NULL,     NULL),                       \
        (41, 'finished',    1,         TRUE,     NULL,         NULL,     '2024-09-01 22:45:00+00'),   \
        (42, 'finished',    2,         TRUE,     NULL,         NULL,     '2024-09-02 22:45:00+00'),   \
        (43, 'finished',    3,         TRUE,     NULL,         NULL,     '2024-09-03 22:45:00+00'),   \
        (44, 'finished',    1,         TRUE,     NULL,         NULL,     '2024-09-01 22:45:00+00'),   \
        (45, 'finished',    2,         TRUE,     NULL,         NULL,     '2024-09-02 22:45:00+00'),   \
        (46, 'finished',    3,         TRUE,     NULL,         NULL,     '2024-09-03 22:45:00+00');"

# And the member entrys for the games
echo "Creating game members for the private games..."
TABLE_NAME="barelyaschema.game_member"
insert_dummy "$TABLE_NAME" \
    "INSERT INTO $TABLE_NAME \
        (id,    user_id,            game_id, points, result, powerup_big, powerup_fast, powerup_slow) VALUES \
        (1,      9,                  1,          17,   'won',     FALSE,      FALSE,       FALSE), \
        (2,      10,                 1,          15,   'lost',    FALSE,      FALSE,       FALSE), \
        (3,      11,                 2,          11,   'won',     FALSE,      FALSE,       FALSE), \
        (4,      12,                 2,           7,   'lost',    FALSE,      FALSE,       FALSE), \
        (5,      13,                 3,           9,   'won',     FALSE,      FALSE,       FALSE), \
        (6,      14,                 3,           5,   'lost',    FALSE,      FALSE,       FALSE), \
        (7,      9,                  4,           5,   'won',     FALSE,      FALSE,       FALSE), \
        (8,      10,                 4,           7,   'lost',    FALSE,      FALSE,       FALSE), \
        (9,      11,                 5,          11,   'won',     FALSE,      FALSE,       FALSE), \
        (10,     12,                 5,           8,   'lost',    FALSE,      FALSE,       FALSE), \
        (11,     13,                 6,          17,   'won',     FALSE,      FALSE,       FALSE), \
        (12,     14,                 6,          15,   'lost',    FALSE,      FALSE,       FALSE), \
        (13,     9,                  7,           8,   'won',     FALSE,      FALSE,       FALSE), \
        (14,     10,                 7,           6,   'lost',    FALSE,      FALSE,       FALSE), \
        (15,     11,                 8,          11,   'won',     FALSE,      FALSE,       FALSE), \
        (16,     12,                 8,           7,   'lost',    FALSE,      FALSE,       FALSE), \
        (17,     13,                 9,          17,   'won',     FALSE,      FALSE,       FALSE), \
        (18,     14,                 9,          15,   'lost',    FALSE,      FALSE,       FALSE), \
        (19,     9,                 10,           6,   'won',     FALSE,      FALSE,       FALSE), \
        (20,     10,                10,           5,   'lost',    FALSE,      FALSE,       FALSE), \
        (21,     11,                11,           8,   'won',     FALSE,      FALSE,       FALSE), \
        (22,     12,                11,           7,   'lost',    FALSE,      FALSE,       FALSE), \
        (23,     13,                12,          11,   'won',     FALSE,      FALSE,       FALSE), \
        (24,     14,                12,           9,   'lost',    FALSE,      FALSE,       FALSE), \
        (25,     9,                 13,           8,   'won',     FALSE,      FALSE,       FALSE), \
        (26,     10,                13,           6,   'lost',    FALSE,      FALSE,       FALSE), \
        (27,     11,                14,          17,   'won',     FALSE,      FALSE,       FALSE), \
        (28,     12,                14,          15,   'lost',    FALSE,      FALSE,       FALSE), \
        (29,     13,                15,           8,   'won',     FALSE,      FALSE,       FALSE), \
        (30,     14,                15,           7,   'lost',    FALSE,      FALSE,       FALSE), \
        (31,     9,                 16,          12,   'won',     FALSE,      FALSE,       FALSE), \
        (32,     10,                16,           9,   'lost',    FALSE,      FALSE,       FALSE), \
        (33,     11,                17,           6,   'won',     FALSE,      FALSE,       FALSE), \
        (34,     12,                17,           5,   'lost',    FALSE,      FALSE,       FALSE), \
        (35,     13,                18,          17,   'won',     FALSE,      FALSE,       FALSE), \
        (36,     14,                18,          15,   'lost',    FALSE,      FALSE,       FALSE), \
        (37,     9,                 19,           7,   'won',     FALSE,      FALSE,       FALSE), \
        (38,     10,                19,           5,   'lost',    FALSE,      FALSE,       FALSE), \
        (39,     11,                20,          11,   'won',     FALSE,      FALSE,       FALSE), \
        (40,     12,                20,           9,   'lost',    FALSE,      FALSE,       FALSE), \
        (41,     13,                21,          17,   'won',     FALSE,      FALSE,       FALSE), \
        (42,     14,                21,          15,   'lost',    FALSE,      FALSE,       FALSE), \
        (43,     9,                 22,          11,   'won',     FALSE,      FALSE,       FALSE), \
        (44,     10,                22,           9,   'lost',    FALSE,      FALSE,       FALSE), \
        (45,     11,                23,           6,   'won',     FALSE,      FALSE,       FALSE), \
        (46,     12,                23,           5,   'lost',    FALSE,      FALSE,       FALSE), \
        (47,     13,                24,           8,   'won',     FALSE,      FALSE,       FALSE), \
        (48,     14,                24,           6,   'lost',    FALSE,      FALSE,       FALSE), \
        (49,     9,                 25,          12,   'won',     FALSE,      FALSE,       FALSE), \
        (50,     10,                25,           9,   'lost',    FALSE,      FALSE,       FALSE), \
        (51,     11,                26,          17,   'won',     FALSE,      FALSE,       FALSE), \
        (52,     12,                26,          15,   'lost',    FALSE,      FALSE,       FALSE), \
        (53,     13,                27,           8,   'won',     FALSE,      FALSE,       FALSE), \
        (54,     14,                27,           7,   'lost',    FALSE,      FALSE,       FALSE), \
        (55,     9,                 28,          11,   'won',     FALSE,      FALSE,       FALSE), \
        (56,     10,                28,           9,   'lost',    FALSE,      FALSE,       FALSE), \
        (57,     11,                29,           7,   'won',     FALSE,      FALSE,       FALSE), \
        (58,     12,                29,           5,   'lost',    FALSE,      FALSE,       FALSE), \
        (59,     13,                30,           5,   'won',     FALSE,      FALSE,       FALSE), \
        (60,     14,                30,           2,   'lost',    FALSE,      FALSE,       FALSE), \
        (61,     11,                31,           8,   'won',     FALSE,      FALSE,       FALSE), \
        (62,     12,                31,           7,   'lost',    FALSE,      FALSE,       FALSE), \
        (63,     13,                32,           0,   'won',     FALSE,      FALSE,       FALSE), \
        (64,     14,                32,           0,   'lost',    FALSE,      FALSE,       FALSE), \
        (65,     9,                 33,           6,   'won',     FALSE,      FALSE,       FALSE), \
        (66,     10,                33,           5,   'lost',    FALSE,      FALSE,       FALSE), \
        (67,     11,                34,           8,   'won',     FALSE,      FALSE,       FALSE), \
        (68,     12,                34,           7,   'lost',    FALSE,      FALSE,       FALSE), \
        (69,     13,                35,          11,   'won',     FALSE,      FALSE,       FALSE), \
        (70,     14,                35,           9,   'lost',    FALSE,      FALSE,       FALSE), \
        (71,     9,                 36,           8,   'won',     FALSE,      FALSE,       FALSE), \
        (72,     10,                36,           6,   'lost',    FALSE,      FALSE,       FALSE), \
        (73,     11,                37,          17,   'won',     FALSE,      FALSE,       FALSE), \
        (74,     12,                37,          15,   'lost',    FALSE,      FALSE,       FALSE), \
        (75,     9,                 38,           0,   'pending', FALSE,      FALSE,       FALSE), \
        (76,     10,                38,           0,   'pending', FALSE,      FALSE,       FALSE), \
        (77,     11,                39,           7,   'pending', FALSE,      FALSE,       FALSE), \
        (78,     12,                39,           5,   'pending', FALSE,      FALSE,       FALSE), \
        (79,     13,                40,          17,   'pending', FALSE,      FALSE,       FALSE), \
        (80,     14,                40,          15,   'pending', FALSE,      FALSE,       FALSE), \
        (81,     9,                 41,           8,   'won',     FALSE,      FALSE,       FALSE), \
        (82,     $ID_AI,            41,           6,   'lost',    FALSE,      FALSE,       FALSE), \
        (83,     10,                42,          11,   'won',     FALSE,      FALSE,       FALSE), \
        (84,     $ID_AI,            42,           8,   'lost',    FALSE,      FALSE,       FALSE), \
        (85,     11,                43,          17,   'won',     FALSE,      FALSE,       FALSE), \
        (86,     $ID_AI,            43,          15,   'lost',    FALSE,      FALSE,       FALSE), \
        (87,     12,                44,           8,   'won',     FALSE,      FALSE,       FALSE), \
        (88,     $ID_FLATMATE,      44,           7,   'lost',    FALSE,      FALSE,       FALSE), \
        (89,     13,                45,           6,   'won',     FALSE,      FALSE,       FALSE), \
        (90,     $ID_FLATMATE,      45,           5,   'lost',    FALSE,      FALSE,       FALSE), \
        (91,     14,                46,           8,   'won',     FALSE,      FALSE,       FALSE), \
        (92,     $ID_FLATMATE,      46,           6,   'lost',    FALSE,      FALSE,       FALSE);"

# Creating dummy chats
echo "Creating 4 dummy conversations..."
TABLE_NAME="barelyaschema.conversation"
insert_dummy "$TABLE_NAME" \
    "INSERT INTO $TABLE_NAME \
        (id, name, is_group_conversation, is_editable) VALUES \
        (107,  NULL, FALSE, FALSE), \
        (108,  NULL, FALSE, FALSE), \
        (109,  NULL, FALSE, FALSE), \
        (110, NULL, FALSE, FALSE);"

echo "Creating conversation members for the dummy conversations..."
TABLE_NAME="barelyaschema.conversation_member"
insert_dummy "$TABLE_NAME" \
	"INSERT INTO $TABLE_NAME \
        (id,    user_id,        conversation_id,    unread_counter) VALUES  \
		(127,     4,              107,                  0),                     \
		(128,     9,              107,                  0),                     \
		(129,     5,              108,                  0),                     \
		(130,     10,             108,                  0),                     \
		(131,     6,              109,                  0),                     \
		(132,     11,             109,                  0),                     \
		(133,     7,              110,                  0),                     \
		(134,     12,             110,                  0);"

# Conversation 7: Restaurant Visit (100 messages)
# Conversation 8: Hello Exchange
# Conversation 9: 10 Messages of 'oye' from user 5
# Conversation 10: Coding School 42 (3 messages)
echo "Creating tons of messages for the conversations..."
TABLE_NAME="barelyaschema.message"
insert_dummy "$TABLE_NAME"                                                                                          \
    "INSERT INTO $TABLE_NAME                                                                                        \
        ( id,  user_id, conversation_id, created_at, seen_at, content) VALUES                                         \
        ( 150,  $ID_OVERLOARDS, 107, '2000-01-01 00:00:00+00', '2000-01-01 00:00:00+00', '**S,3,8**'),                      \
        ( 151,  $ID_OVERLOARDS, 108, '2000-01-01 00:00:00+00', '2000-01-01 00:00:00+00', '**S,4,9**'),                      \
        ( 152,  $ID_OVERLOARDS, 109, '2000-01-01 00:00:00+00', '2000-01-01 00:00:00+00', '**S,5,10**'),                      \
        ( 153,  $ID_OVERLOARDS, 110, '2000-01-01 00:00:00+00', '2000-01-01 00:00:00+00', '**S,6,11**'),                      \
        ( 154,  4, 107, '2024-01-01 10:00:00+00', '2024-01-01 10:20:00+00', 'Hey, where should we eat?'), \
        ( 155,  9, 107, '2024-01-01 10:01:00+00', '2024-01-01 10:25:00+00', 'How about Italian?'), \
        ( 156,  4, 107, '2024-01-01 10:05:00+00', '2024-01-01 10:30:00+00', 'Sure, sounds great!'), \
        ( 157,  9, 107, '2024-01-01 10:10:00+00', '2024-01-01 10:35:00+00', 'What time works for you?'), \
        ( 158,  4, 107, '2024-01-01 10:15:00+00', '2024-01-01 10:45:00+00', 'Tonight at 7?'), \
        ( 159,  9, 107, '2024-01-01 10:20:00+00', '2024-01-01 10:55:00+00', 'Perfect, see you then!'), \
        ( 160,  4, 107, '2024-01-01 11:00:00+00', '2024-01-01 11:30:00+00', 'I’ll book a table.'), \
        ( 161,  9, 107, '2024-01-01 11:05:00+00', '2024-01-01 11:40:00+00', 'Thanks!'), \
        ( 162,  4, 107, '2024-01-01 12:00:00+00', '2024-01-01 12:40:00+00', 'Do you want starters?'), \
        ( 163,  9, 107, '2024-01-01 12:10:00+00', '2024-01-01 12:50:00+00', 'Yes, garlic bread!'), \
        ( 164,  4, 107, '2024-01-01 13:00:00+00', '2024-01-01 13:40:00+00', 'Same here!'), \
        ( 165,  9, 107, '2024-01-01 13:05:00+00', '2024-01-01 13:50:00+00', 'See you soon.'), \
        ( 166,  4, 107, '2024-01-01 14:00:00+00', '2024-01-01 14:40:00+00', 'Looking forward to it.'), \
        ( 167,  9, 107, '2024-01-01 14:10:00+00', '2024-01-01 14:50:00+00', 'What’s the dress code?'), \
        ( 168,  4, 107, '2024-01-01 15:00:00+00', '2024-01-01 15:40:00+00', 'Casual is fine.'), \
        ( 169,  9, 107, '2024-01-01 15:10:00+00', '2024-01-01 15:50:00+00', 'Okay, cool!'), \
        ( 170,  4, 107, '2024-01-01 16:00:00+00', '2024-01-01 16:40:00+00', 'Booked!'), \
        ( 171,  9, 107, '2024-01-01 16:10:00+00', '2024-01-01 16:50:00+00', 'You’re awesome!'), \
        ( 172,  4, 107, '2024-01-01 17:00:00+00', '2024-01-01 17:40:00+00', 'See you soon.'), \
        ( 173,  9, 107, '2024-01-01 17:10:00+00', '2024-01-01 17:50:00+00', 'Bye!'), \
        ( 174,  4, 107, '2024-01-02 10:00:00+00', '2024-01-02 10:30:00+00', 'I’m on my way.'), \
        ( 175,  9, 107, '2024-01-02 10:05:00+00', '2024-01-02 10:40:00+00', 'Me too!'), \
        ( 176,  4, 107, '2024-01-02 11:00:00+00', '2024-01-02 11:30:00+00', 'I’m on my way!'), \
        ( 177,  9, 107, '2024-01-02 11:05:00+00', '2024-01-02 11:45:00+00', 'Me too, see you soon!'), \
        ( 178,  4, 107, '2024-01-02 12:00:00+00', '2024-01-02 12:40:00+00', 'Did you find parking?'), \
        ( 179,  9, 107, '2024-01-02 12:10:00+00', '2024-01-02 12:50:00+00', 'Yeah, a bit crowded though.'), \
        ( 180,  4, 107, '2024-01-02 12:20:00+00', '2024-01-02 13:00:00+00', 'I’m inside already.'), \
        ( 181,  9, 107, '2024-01-02 12:25:00+00', '2024-01-02 13:05:00+00', 'Ordering drinks, want anything?'), \
        ( 182,  4, 107, '2024-01-02 12:30:00+00', '2024-01-02 13:10:00+00', 'Just water for now.'), \
        ( 183,  9, 107, '2024-01-02 12:35:00+00', '2024-01-02 13:15:00+00', 'Got it, see you in a sec!'), \
        ( 184,  4, 107, '2024-01-02 12:45:00+00', '2024-01-02 13:25:00+00', 'What are you thinking of eating?'), \
        ( 185,  9, 107, '2024-01-02 12:50:00+00', '2024-01-02 13:30:00+00', 'The lasagna sounds good.'), \
        ( 186,  4, 107, '2024-01-02 13:00:00+00', '2024-01-02 13:40:00+00', 'I might go for the pizza.'), \
        ( 187,  9, 107, '2024-01-02 13:05:00+00', '2024-01-02 13:45:00+00', 'Nice choice!'), \
        ( 188,  4, 107, '2024-01-02 13:10:00+00', '2024-01-02 13:50:00+00', 'Do we want dessert?'), \
        ( 189,  9, 107, '2024-01-02 13:15:00+00', '2024-01-02 13:55:00+00', 'Tiramisu maybe?'), \
        ( 190,  4, 107, '2024-01-02 13:20:00+00', '2024-01-02 14:00:00+00', 'Sounds perfect!'), \
        ( 191,  9, 107, '2024-01-02 13:25:00+00', '2024-01-02 14:05:00+00', 'Great dinner, thanks for joining!'), \
        ( 192,  4, 107, '2024-01-02 13:30:00+00', '2024-01-02 14:10:00+00', 'Always a pleasure.'), \
        ( 193,  9, 107, '2024-01-02 13:35:00+00', '2024-01-02 14:15:00+00', 'We should do this again soon.'), \
        ( 194,  4, 107, '2024-01-02 13:40:00+00', '2024-01-02 14:20:00+00', 'Agreed, let’s pick a date!'), \
        ( 195,  9, 107, '2024-01-02 13:45:00+00', '2024-01-02 14:25:00+00', 'How about next week?'), \
        ( 196,  4, 107, '2024-01-02 13:50:00+00', '2024-01-02 14:30:00+00', 'Works for me!'), \
        ( 197,  9, 107, '2024-01-02 14:00:00+00', '2024-01-02 14:40:00+00', 'See you then!'), \
        ( 198,  4, 107, '2024-01-02 14:05:00+00', '2024-01-02 14:45:00+00', 'See you!'), \
        ( 199,  9, 107, '2024-01-02 15:00:00+00', '2024-01-02 15:40:00+00', 'Take care!'), \
        ( 200,  4, 107, '2024-01-02 15:05:00+00', '2024-01-02 15:45:00+00', 'You too!'), \
        ( 201,  9, 107, '2024-01-02 15:10:00+00', '2024-01-02 15:50:00+00', 'Bye!'), \
        ( 202,  4, 107, '2024-01-02 15:15:00+00', '2024-01-02 15:55:00+00', 'Bye!'), \
        ( 203,  9, 107, '2024-01-02 15:20:00+00', '2024-01-02 16:00:00+00', 'Talk soon.'), \
        ( 204,  4, 107, '2024-01-02 15:25:00+00', '2024-01-02 16:05:00+00', 'Absolutely!'), \
        ( 205,  9, 107, '2024-01-03 11:00:00+00', '2024-01-03 11:40:00+00', 'Hey, did you enjoy the food?'), \
        ( 206,  4, 107, '2024-01-03 11:05:00+00', '2024-01-03 11:45:00+00', 'Yes, it was amazing!'), \
        ( 207,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'Glad to hear that!'), \
        ( 208,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'Let’s go back soon.'), \
        ( 209,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'Lets play ping pong!'), \
        ( 210,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'Lets go: ping'), \
        ( 211,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        ( 212,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 213,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        ( 214,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 215,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        ( 216,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 217,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        ( 218,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 219,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        ( 220,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 221,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        ( 222,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 223,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        ( 224,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 225,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        ( 226,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 227,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        ( 228,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 229,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        ( 230,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 231,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        ( 232,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 233,  9, 107, '2024-01-03 12:00:00+00', '2024-01-03 12:40:00+00', 'pong!'), \
        ( 234,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 235,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 236,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 237,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 238,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 239,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 240,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 241,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 242,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 243,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 244,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 245,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 246,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 247,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 248,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 249,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 250,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 251,  4, 107, '2024-01-03 12:05:00+00', '2024-01-03 12:45:00+00', 'ping!'), \
        ( 252,  4, 107, '2024-01-05 10:00:00+00', '2024-01-05 10:40:00+00', 'Next time’s on me!'), \
        ( 253,  9, 107, '2024-01-05 10:05:00+00', '2024-01-05 10:45:00+00', 'Deal!'), \
        ( 254,  5, 108, '2024-02-01 12:00:00+00', '2024-02-01 12:20:00+00', 'Hello?'), \
        ( 255, 10, 108, '2024-02-01 12:01:00+00', '2024-02-01 12:30:00+00', 'Hello!'), \
        ( 256,  6, 109, '2024-02-01 13:00:00+00', '2024-02-01 13:20:00+00', 'Oye'), \
        ( 257,  6, 109, '2024-02-01 13:10:00+00', '2024-02-01 13:30:00+00', 'Oye'), \
        ( 258,  6, 109, '2024-02-01 13:20:00+00', '2024-02-01 13:50:00+00', 'Oye'), \
        ( 259,  6, 109, '2024-02-01 13:30:00+00', '2024-02-01 14:00:00+00', 'Oye'), \
        ( 260,  6, 109, '2024-02-01 13:40:00+00', '2024-02-01 14:10:00+00', 'Oye'), \
        ( 261,  6, 109, '2024-02-01 13:50:00+00', '2024-02-01 14:20:00+00', 'Oye'), \
        ( 262,  6, 109, '2024-02-01 14:00:00+00', '2024-02-01 14:30:00+00', 'Oye'), \
        ( 263,  6, 109, '2024-02-01 14:10:00+00', '2024-02-01 14:40:00+00', 'Oye'), \
        ( 264,  6, 109, '2024-02-01 14:20:00+00', '2024-02-01 14:50:00+00', 'Oye'), \
        ( 265,  6, 109, '2024-02-01 14:30:00+00', '2024-02-01 15:00:00+00', 'Oye'), \
        ( 266,  7, 110, '2024-03-01 10:00:00+00', '2024-03-01 10:30:00+00', 'Have you heard of 42?'), \
        ( 267, 12, 110, '2024-03-01 10:01:00+00', '2024-03-01 10:31:00+00', 'Yeah, it’s amazing!'), \
        ( 268, 12, 110, '2024-03-01 14:10:00+00', '2024-03-01 14:40:00+00', 'Let’s apply together!');"

# Creating finished tournament games
# Tournament 1: Round Robin between players:9,10,11,12
# Tournament 2: Round Robin between players:4-12
# Tournament 3: Round Robin between players:4,5,6
echo "Creating finished tournament games..."
echo -e "CREATING GAMES:\tTournament 1: Round Robin between players:9,10,11,12"
echo -e "CREATING GAMES:\tTournament 2: Round Robin between players:4,5,6,7,8,9,10,11,12"
echo -e "CREATING GAMES:\tTournament 3: Round Robin between players:4,5,6"
TABLE_NAME="barelyaschema.game"
insert_dummy "$TABLE_NAME" \
    "INSERT INTO $TABLE_NAME \
        (id,    state,          type,            map_number, powerups, tournament_id, deadline, finish_time) VALUES \
        -- Round Robin Matches (6 games)
        (100, 'finished',       'normal',          2, TRUE, 1, '2024-07-01 13:29:00+00', '2024-07-01 13:30:00+00'), \
        (101, 'finished',       'normal',          2, TRUE, 1, '2024-07-01 14:29:00+00', '2024-07-01 14:30:00+00'), \
        (102, 'finished',       'normal',          2, TRUE, 1, '2024-07-01 15:29:00+00', '2024-07-01 15:30:00+00'), \
        (103, 'finished',       'normal',          2, TRUE, 1, '2024-07-01 16:29:00+00', '2024-07-01 16:30:00+00'), \
        (104, 'finished',       'normal',          2, TRUE, 1, '2024-07-01 17:29:00+00', '2024-07-01 17:30:00+00'), \
        (105, 'finished',       'normal',          2, TRUE, 1, '2024-07-01 18:29:00+00', '2024-07-01 18:30:00+00'), \
        -- Semi-Finale
        (106, 'finished',       'semifinal',       2, TRUE, 1, '2024-07-01 19:29:00+00', '2024-07-01 19:30:00+00'), \
        (140, 'finished',       'semifinal',       2, TRUE, 1, '2024-07-01 19:29:00+00', '2024-07-01 19:30:00+00'), \
        -- Finale (1 game)
        (107, 'finished',       'thirdplace',      2, TRUE, 1, '2024-07-01 20:29:00+00', '2024-07-01 20:30:00+00'), \
        (141, 'finished',       'final',           2, TRUE, 1, '2024-07-01 20:30:00+00', '2024-07-01 20:31:00+00'), \
        -- Tournament 2
        -- Round 1
        (108, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 07:59:00+00', '2024-08-01 08:00:00+00'), \
        (109, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 08:29:00+00', '2024-08-01 08:30:00+00'), \
        (110, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 08:59:00+00', '2024-08-01 09:00:00+00'), \
        (111, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 09:29:00+00', '2024-08-01 09:30:00+00'), \
        (112, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 09:59:00+00', '2024-08-01 10:00:00+00'), \
        (113, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 10:29:00+00', '2024-08-01 10:30:00+00'), \
        (114, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 10:59:00+00', '2024-08-01 11:00:00+00'), \
        (115, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 11:29:00+00', '2024-08-01 11:30:00+00'), \
        (116, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 11:59:00+00', '2024-08-01 12:00:00+00'), \
        (117, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 12:29:00+00', '2024-08-01 12:30:00+00'), \
        (118, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 12:59:00+00', '2024-08-01 13:00:00+00'), \
        (119, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 13:29:00+00', '2024-08-01 13:30:00+00'), \
        (120, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 13:59:00+00', '2024-08-01 14:00:00+00'), \
        (121, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 14:29:00+00', '2024-08-01 14:30:00+00'), \
        (122, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 14:59:00+00', '2024-08-01 15:00:00+00'), \
        (123, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 15:29:00+00', '2024-08-01 15:30:00+00'), \
        (124, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 15:59:00+00', '2024-08-01 16:00:00+00'), \
        (125, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 16:29:00+00', '2024-08-01 16:30:00+00'), \
        (126, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 16:59:00+00', '2024-08-01 17:00:00+00'), \
        (127, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 17:29:00+00', '2024-08-01 17:30:00+00'), \
        (128, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 17:59:00+00', '2024-08-01 18:00:00+00'), \
        (129, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 18:29:00+00', '2024-08-01 18:30:00+00'), \
        (130, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 18:59:00+00', '2024-08-01 19:00:00+00'), \
        (131, 'finished',       'normal',          4, FALSE, 2, '2024-08-01 19:29:00+00', '2024-08-01 19:30:00+00'), \
        -- Semi-Finale 1
        (132, 'finished',       'semifinal',       4, FALSE, 2, '2024-08-01 19:59:00+00', '2024-08-01 20:00:00+00'), \
        -- Semi-Finale 2
        (133, 'finished',       'semifinal',       4, FALSE, 2, '2024-08-01 20:29:00+00', '2024-08-01 20:30:00+00'), \
        -- Third Place
        (134, 'finished',       'thirdplace',      4, FALSE, 2, '2024-08-01 20:59:00+00', '2024-08-01 21:00:00+00'), \
        -- Finale
        (135, 'finished',       'final',           4, FALSE, 2, '2024-08-01 20:59:00+00', '2024-08-01 21:00:00+00'), \
        -- Tournament 3
        (136, 'finished',       'normal',          3, FALSE, 3, '2024-09-01 07:59:00+00', '2024-09-01 08:00:00+00'), \
        (137, 'finished',       'normal',          3, FALSE, 3, '2024-09-01 08:29:00+00', '2024-09-01 08:30:00+00'), \
        (138, 'finished',       'normal',          3, FALSE, 3, '2024-09-01 08:59:00+00', '2024-09-01 09:00:00+00'), \
        -- Final
        (139, 'finished',       'final',           3, FALSE, 3, '2024-09-01 12:29:00+00', '2024-09-01 12:29:00+00');"

# Creating GameMembers for the tournament games
echo -e "CREATING GAME MEMBERS\tTournament 1: Round Robin between players:9,10,11,12"
echo -e "CREATING GAME MEMBERS\tTournament 2: Round Robin between players:4,5,6,7,8,9,10,11,12"
echo -e "CREATING GAME MEMBERS\tTournament 3: Round Robin between players:4,5,6"
TABLE_NAME="barelyaschema.game_member"
insert_dummy "$TABLE_NAME" \
    "INSERT INTO $TABLE_NAME \
        (id, user_id, game_id, points, result, powerup_big, powerup_fast, powerup_slow) VALUES \
        -- Game 100
        (181,  9, 100, 11, 'won', TRUE, FALSE, FALSE), \
        (182, 10, 100, 9,  'lost', FALSE, TRUE, FALSE), \
        -- Game 101
        (183,  9, 101, 13, 'won', FALSE, FALSE, TRUE), \
        (184, 11, 101, 11, 'lost', TRUE, TRUE, FALSE), \
        -- Game 102
        (185,  9, 102, 11, 'won', FALSE, TRUE, FALSE), \
        (186, 12, 102, 9,  'lost', TRUE, FALSE, TRUE), \
        -- Game 103
        (187, 10, 103, 11, 'won', TRUE, FALSE, FALSE), \
        (188, 11, 103, 8,  'lost', FALSE, TRUE, FALSE), \
        -- Game 104
        (189, 10, 104, 13, 'won', FALSE, TRUE, FALSE), \
        (190, 12, 104, 11, 'lost', TRUE, FALSE, TRUE), \
        -- Game 105
        (191, 11, 105, 11, 'won', FALSE, FALSE, TRUE), \
        (192, 12, 105, 9,  'lost', TRUE, TRUE, FALSE), \
        -- Semi-Finales
        (193, 10, 106, 15, 'won', TRUE, FALSE, TRUE), \
        (194, 11, 106, 13, 'lost', FALSE, TRUE, FALSE), \
        (261,  9, 140, 11, 'won', FALSE, TRUE, FALSE), \
        (262, 12, 140, 9,  'lost', TRUE, FALSE, TRUE), \
        -- Finale (Game 107)
        (263,  9, 141, 11, 'won', TRUE, TRUE, FALSE), \
        (264, 10, 141, 9,  'lost', FALSE, FALSE, TRUE), \
        -- Third place
        (195, 11, 107, 11, 'won', FALSE, FALSE, TRUE), \
        (196, 12, 107, 9,  'lost', FALSE, FALSE, TRUE), \
        -- Tournament 2
        -- Round 1
        (197,  4, 108, 11, 'won', FALSE, FALSE, FALSE), \
        (198,  5, 108, 9, 'lost', FALSE, FALSE, FALSE), \
        (199,  6, 109, 13, 'won', FALSE, FALSE, FALSE), \
        (200,  7, 109, 11, 'lost', FALSE, FALSE, FALSE), \
        (201,  8, 110, 11, 'won', FALSE, FALSE, FALSE), \
        (202,  9, 110, 9, 'lost', FALSE, FALSE, FALSE), \
        (203, 10, 111, 13, 'won', FALSE, FALSE, FALSE), \
        (204, 11, 111, 11, 'lost', FALSE, FALSE, FALSE), \
        (205,  4, 112, 11, 'won', FALSE, FALSE, FALSE), \
        (206,  6, 112, 9, 'lost', FALSE, FALSE, FALSE), \
        (207,  7, 113, 13, 'won', FALSE, FALSE, FALSE), \
        (208,  8, 113, 11, 'lost', FALSE, FALSE, FALSE), \
        (209,  9, 114, 11, 'won', FALSE, FALSE, FALSE), \
        (210, 10, 114, 9, 'lost', FALSE, FALSE, FALSE), \
        (211, 11, 115, 13, 'won', FALSE, FALSE, FALSE), \
        (212, 12, 115, 11, 'lost', FALSE, FALSE, FALSE), \
        (213,  4, 116, 11, 'won', FALSE, FALSE, FALSE), \
        (214,  7, 116, 9, 'lost', FALSE, FALSE, FALSE), \
        (215,  8, 117, 13, 'won', FALSE, FALSE, FALSE), \
        (216,  9, 117, 11, 'lost', FALSE, FALSE, FALSE), \
        (217, 10, 118, 11, 'won', FALSE, FALSE, FALSE), \
        (218, 11, 118, 9, 'lost', FALSE, FALSE, FALSE), \
        (219,  5, 119, 13, 'won', FALSE, FALSE, FALSE), \
        (220,  6, 119, 11, 'lost', FALSE, FALSE, FALSE), \
        (221,  7, 120, 11, 'won', FALSE, FALSE, FALSE), \
        (222,  8, 120, 9, 'lost', FALSE, FALSE, FALSE), \
        (223,  9, 121, 13, 'won', FALSE, FALSE, FALSE), \
        (224, 10, 121, 11, 'lost', FALSE, FALSE, FALSE), \
        (225, 11, 122, 11, 'won', FALSE, FALSE, FALSE), \
        (226, 12, 122, 9, 'lost', FALSE, FALSE, FALSE), \
        (227,  4, 123, 13, 'won', FALSE, FALSE, FALSE), \
        (228,  9, 123, 11, 'lost', FALSE, FALSE, FALSE), \
        (229, 10, 124, 11, 'won', FALSE, FALSE, FALSE), \
        (230,  5, 124, 9, 'lost', FALSE, FALSE, FALSE), \
        (231,  6, 125, 13, 'won', FALSE, FALSE, FALSE), \
        (232, 11, 125, 11, 'lost', FALSE, FALSE, FALSE), \
        (233, 12, 126, 11, 'won', FALSE, FALSE, FALSE), \
        (234,  7, 126, 9, 'lost', FALSE, FALSE, FALSE), \
        (235,  8, 127, 13, 'won', FALSE, FALSE, FALSE), \
        (236,  4, 127, 11, 'lost', FALSE, FALSE, FALSE), \
        (237,  5, 128, 11, 'won', FALSE, FALSE, FALSE), \
        (238,  6, 128, 9, 'lost', FALSE, FALSE, FALSE), \
        (239,  7, 129, 13, 'won', FALSE, FALSE, FALSE), \
        (240,  8, 129, 11, 'lost', FALSE, FALSE, FALSE), \
        (241,  9, 130, 11, 'won', FALSE, FALSE, FALSE), \
        (242, 10, 130, 9, 'lost', FALSE, FALSE, FALSE), \
        (243, 11, 131, 13, 'won', FALSE, FALSE, FALSE), \
        (244, 12, 131, 11, 'lost', FALSE, FALSE, FALSE), \
        -- Semi-Finale 1
        (245, 9, 132, 13, 'lost', FALSE, FALSE, FALSE), \
        (246, 4, 132, 15, 'won',  FALSE, FALSE, FALSE), \
        -- Semi-Finale 2
        (247, 6, 133, 11, 'won', FALSE, FALSE, FALSE), \
        (248, 8, 133, 9, 'lost', FALSE, FALSE, FALSE), \
        -- Third Place
        (249, 9, 134, 11, 'won', FALSE, FALSE, FALSE), \
        (250, 8, 134, 9, 'lost', FALSE, FALSE, FALSE), \
        -- Finale
        (251, 4, 135, 15, 'won',  FALSE, FALSE, FALSE), \
        (252, 6, 135, 13, 'lost', FALSE, FALSE, FALSE), \
        -- Tournament 3
        (253, 4, 136, 11, 'won',  FALSE, FALSE, FALSE), \
        (254, 5, 136, 9, 'lost',  FALSE, FALSE, FALSE),
        (255, 4, 137, 13, 'won',  FALSE, FALSE, FALSE), \
        (256, 6, 137, 11, 'lost', FALSE, FALSE, FALSE), \
        (257, 5, 138, 11, 'won',  FALSE, FALSE, FALSE), \
        (258, 6, 138, 5,  'lost', FALSE, FALSE, FALSE), \
        -- Final
        (259, 4, 139, 2,  'lost', FALSE, FALSE, FALSE), \
        (260, 5, 139, 11, 'won',  FALSE, FALSE, FALSE);"

# Create the actual tournament
echo -e "CREATING TOURNAMENTS:\tTournament 1: Round Robin between players:9,10,11,12"
echo -e "CREATING TOURNAMENTS:\tTournament 2: Round Robin between players:4,5,6,7,8,9,10,11,12"
echo -e "CREATING TOURNAMENTS:\tTournament 3: Round Robin between players:4,5,6"
echo -e "CREATING TOURNAMENTS:\tTournament 4: Round Robin Public in setup"
echo -e "CREATING TOURNAMENTS:\tTournament 5: Round Robin Private in setup"
TABLE_NAME="barelyaschema.tournament"
insert_dummy "$TABLE_NAME" \
    "INSERT INTO $TABLE_NAME \
        (id, state,     name,                       local_tournament, public_tournament, map_number, powerups,  finish_time) VALUES        \
        (1, 'finished', 'Players-8,9,10,11',        FALSE,            TRUE,              2,          TRUE,      '2024-07-01 20:30:00+00'), \
        (2, 'finished', 'Players-4-12',             FALSE,            FALSE,             4,          FALSE,     '2024-08-01 21:00:00+00'), \
        (3, 'finished', 'Players-4,5,6',            FALSE,            FALSE,             3,          FALSE,     '2024-09-01 21:00:00+00'), \
        (4, 'setup',    'Let’s-play!?',             FALSE,            TRUE,              3,          TRUE,      NULL),                     \
        (5, 'setup',    'This-is-privateone!;)',    FALSE,            FALSE ,            1,          TRUE,      NULL);"

# Create the tournament members
echo -e "CREATING TOURNAMENT MEMBERS:\tTournament 1: Round Robin between players:9,10,11,12"
echo -e "CREATING TOURNAMENT MEMBERS:\tTournament 2: Round Robin between players:4,5,6,7,8,9,10,11,12"
echo -e "CREATING TOURNAMENT MEMBERS:\tTournament 3: Round Robin between players:4,5,6"
echo -e "CREATING TOURNAMENT MEMBERS:\tTournament 4: Round Robin Public in setup"
echo -e "CREATING TOURNAMENT MEMBERS:\tTournament 5: Round Robin Private in setup"
TABLE_NAME="barelyaschema.tournament_member"
insert_dummy "$TABLE_NAME"                                                                                                   \
    "INSERT INTO $TABLE_NAME                                                                                                 \
        (id, user_id, tournament_id, tournament_alias, is_admin, accepted, played_games, won_games, win_points, rank) VALUES \
        -- Tournament 1 Members
        (1,    9,        1,              'Player 9',     TRUE,    TRUE,         4,          4,          8,        1), \
        (2,    10,       1,              'Player 10',    FALSE,   TRUE,         4,          2,          5,        2), \
        (3,    11,       1,              'Player 11',    FALSE,   TRUE,         4,          1,          2,        3), \
        (4,    12,       1,              'Player 12',    FALSE,   TRUE,         4,          0,          0,        4), \
        -- Tournament 2 Members
        (5,    4,        2,              'Player 4',     TRUE,    TRUE,         6,          6,          18,       1), \
        (6,    8,        2,              'Player 8',     FALSE,   TRUE,         6,          3,          12,       2), \
        (7,    6,        2,              'Player 6',     FALSE,   TRUE,         6,          3,          9,        3), \
        (8,    9,        2,              'Player 9',     FALSE,   TRUE,         6,          3,          9,        4), \
        (9,    11,       2,              'Player 11',    FALSE,   TRUE,         6,          3,          8,        5), \
        (10,   7,        2,              'Player 7',     FALSE,   TRUE,         6,          2,          8,        6), \
        (11,   5,        2,              'Player 5',     FALSE,   TRUE,         6,          2,          6,        7), \
        (12,   10,       2,              'Player 10',    FALSE,   TRUE,         6,          2,          6,        8), \
        (13,   12,       2,              'Player 12',    FALSE,   TRUE,         6,          1,          4,        9), \
        -- Tournament 3 Members
        (14,   4,        3,              'Player 4',     TRUE,    TRUE,         2,          2,          4,        1), \
        (15,   5,        3,              'Player 5',     FALSE,   TRUE,         2,          1,          6,        2), \
        (16,   6,        3,              'Player 6',     FALSE,   TRUE,         2,          0,          0,        3), \
        -- Tournament 4 and 5 are in setup and no games are completed
        (17,   11,       4,              'Player 11',    TRUE,    TRUE,         0,          0,          0,        0), \
        (18,   12,       4,              'Player 12',    FALSE,   TRUE,         0,          0,          0,        0), \
        (19,   4,        5,              'Player 4',     TRUE,    TRUE,         0,          0,          0,        0), \
        (20,   5,        5,              'Player 5',     FALSE,   FALSE,        0,          0,          0,        0), \
        (21,   6,        5,              'Player 6',     FALSE,   TRUE,         0,          0,          0,        0);"

# Make some friends so that xico can create tournaments
echo -e "CREATING FRIENDSHIPS:\tXico is friends with 4, 5, 6, 7, 8"
TABLE_NAME="barelyaschema.is_cool_with"
insert_dummy "$TABLE_NAME"                                      \
	"INSERT INTO $TABLE_NAME                                    \
        (id,    requester_id,   requestee_id, status) VALUES    \
        (39,    13,             4,            'accepted'),        \
        (40,    13,             5,            'accepted'),        \
        (41,    13,             6,            'accepted'),        \
        (42,    13,             7,            'accepted'),        \
        (43,    13,             8,            'accepted');"

print_header "RESETING SEQUENCES..."
for table in "${ALL_TABLES[@]}"; do
    reset_sequence "$table"
done