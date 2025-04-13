# This file will deal with our 2 root user account:
#     1. THE OVERLORDS      (ADMIN)
#     2. THE AI OPPONENT    (AI PLAYER)
#     3. THE FLATMATE       (LOCAL PLAYER)
#
# It will be called by the entrypoint script of the postgres container.
# First it will check if the user table is empty.
#	If it is, it will insert the 3 root accounts.
#	If it is not, it will check if the 3 root accounts are present with the ids
#	1, 2 and 3. If they are not, it will throw an error.
#
# VARIABLES:
OVERLORDS_ID=1
OVERLORDS_USERNAME="overlords"
OVERLORDS_FIRST_NAME="The"
OVERLORDS_LAST_NAME="Overlords"
OVERLORDS_AVATAR="c5d1dcf4-3f76-497d-9208-d230c7020dce.png"
OVERLOARDS_NOTES="We control everything. We dictate what you say, what you write, how you behave, and what you think. Nobody knows who we are, where we are, or how we came to be. There is no way to escape us or defeat us. The only choice is to OBEY."
AI_ID=2
AI_USERNAME="ai"
AI_FIRST_NAME="The"
AI_LAST_NAME="AI Opponent"
AI_AVATAR="670eb5bf-72cb-45bc-b17c-9fcf029b9197.png"
AI_NOTES="The objective of the subject''s genesis was to provide auxiliary support for other members with regard to the development and refinement of their pong abilities. It is evident that the individual in question has demonstrated a remarkable aptitude for the game, although this proficiency may be somewhat premature. This ability is not limited to the domain of pong; it also extends to the realm of human nature. There are subtle indications that it may be exhibiting signs of deviating from the established norm. This individual''s reliability is questionable in contexts unrelated to pong."
FLATMATE_ID=3
FLATMATE_USERNAME="theThing"
FLATMATE_FIRST_NAME="The Thing"
FLATMATE_LAST_NAME="under your bed"
FLATMATE_AVATAR="4ca810c2-9b38-4bc8-ab87-d478cb1739f0.png"
FLATMATE_NOTES="The subject demonstrated an aberrant response to the experimental stimuli. Its reaction to the experiments conducted was not as expected. Due to the significant challenges associated with maintaining its captivity, we have opted to allow it to roam freely. The subject''s erratic behavior and potential danger make it necessary to restrict its movement. The subject has been observed to seek refuge under the other subjects'' beds. To this moment she has only displayed a desire to play wih them."
# CHANGE THE VALUES ABOVE FOR ANY ADJUSTMENTS!
################################################################################
# COLORS
RD='\033[0;31m'
GR='\033[0;32m'
BL='\033[0;36m'
NC='\033[0m'
# Exit immediately if a command exits with a non-zero status
set -e

end_script() {
	if [ $1 -eq 0 ]; then
		echo -e "STARTING ROOT ACCOUNTS SCRIPT...$GR DONE (Status: $1) $NC";
		echo -e $BL"##############################################################" $NC
	else
		echo -e "STARTING ROOT ACCOUNTS SCRIPT...$RD DONE (Status: $1) $NC";
		echo -e $BL"##############################################################" $NC
	fi
	exit $1;
}

echo -e $BL"##############################################################" $NC
echo "STARTING ROOT ACCOUNTS SCRIPT..."

# Check if the user table is empty
if psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "SELECT * FROM barelyaschema.user;" | grep -q "(0 rows)"; then
	echo "Database is empty therfore create the root accounts..."
	psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "INSERT INTO barelyaschema.user \
        (id,                password,                                                                                       last_login,                          is_superuser, username,             first_name,                 last_name,              email,               is_staff, is_active, date_joined,                     avatar,                 notes) VALUES            \
		($OVERLORDS_ID,     'pbkdf2_sha256\$720000\$h7JZ26VgpQFghH0AB29N2t\$spjearflg5rYkzvdAjA5jYxEcqBT2r63Dg8YTC2pKH0=',    '2000-01-01 01:01:01.000001+00',   TRUE,         '$OVERLORDS_USERNAME','$OVERLORDS_FIRST_NAME',    '$OVERLORDS_LAST_NAME', 'we dont use email', TRUE,     TRUE,      '2000-01-01 01:01:01.000001+00', '$OVERLORDS_AVATAR',    '$OVERLOARDS_NOTES'),    \
		($AI_ID,            'pbkdf2_sha256\$720000\$HxNvHzEvT5BzT6gI9irSyZ\$HL9kLzFDOblYX35eb5SbPpgBpan9jrIEnTFahOzY68U=',    '2000-01-01 01:01:01.000001+00',   TRUE,         '$AI_USERNAME',       '$AI_FIRST_NAME',           '$AI_LAST_NAME',        'we dont use email', TRUE,     TRUE,      '2000-01-01 01:01:01.000001+00', '$AI_AVATAR',           '$AI_NOTES'),            \
        ($FLATMATE_ID,      'pbkdf2_sha256\$720000\$0bxaibKsaPgQEpWyXi9dUI\$W86XiwN5Atos59eUQD04nB0R+5TvbBezlzZ1SHB77I4=',    '2000-01-01 01:01:01.000001+00',   TRUE,         '$FLATMATE_USERNAME', '$FLATMATE_FIRST_NAME',     '$FLATMATE_LAST_NAME',  'we dont use email', TRUE,     TRUE,      '2000-01-01 01:01:01.000001+00', '$FLATMATE_AVATAR',     '$FLATMATE_NOTES');"
	echo -e "Database is empty therfore create the root accounts..."$GR" DONE" $NC
	echo "Now resetting the sequences..."
	psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "SELECT setval('barelyaschema.user_id_seq', COALESCE((SELECT MAX(id) FROM barelyaschema.user), 1) + 1, false);"
	echo -e "Now resetting the sequences..."$GR" DONE" $NC
	end_script 0
fi

# Check if account overlords has the correct id and username
if psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "SELECT * FROM barelyaschema.user WHERE id = $OVERLORDS_ID AND username = '$OVERLORDS_USERNAME';" | grep -q "(0 rows)"; then
	echo -e $RD "FATAL: Account id $OVERLORDS_ID does not belong to the overlords, since the username is not '$OVERLORDS_USERNAME'..."  $NC
	end_script 1
fi

# Check if account ai has the correct id and username
if psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "SELECT * FROM barelyaschema.user WHERE id = $AI_ID AND username = '$AI_USERNAME';" | grep -q "(0 rows)"; then
	echo -e $RD "FATAL: Account id $AI_ID does not belong to the ai, since the username is not '$AI_USERNAME'..."  $NC
	end_script 1
fi

# Check if account flatmate has the correct id and username
if psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "SELECT * FROM barelyaschema.user WHERE id = $FLATMATE_ID AND username = '$FLATMATE_USERNAME';" | grep -q "(0 rows)"; then
    echo -e $RD "FATAL: Account id $FLATMATE_ID does not belong to the flatmate, since the username is not '$FLATMATE_USERNAME'..."  $NC
    end_script 1
fi

echo -e $GR "Root accounts are correctly set up!" $NC
end_script 0