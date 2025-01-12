# This file will deal with our 2 root user account:
#     1. THE OVERLORDS
#     2. THE AI OPPONENT
#
# It will be called by the entrypoint script of the postgres container.
# First it will check if the user table is empty.
#	If it is, it will insert the 2 root accounts.
#	If it is not, it will check if the 2 root accounts are present with the ids
#	1 and 2. If they are not, it will throw an error.
#
# VARIABLES:
OVERLORDS_ID=1
OVERLORDS_USERNAME="overlords"
OVERLORDS_FIRST_NAME="The"
OVERLORDS_LAST_NAME="Overlords"
OVERLORDS_AVATAR="c5d1dcf4-3f76-497d-9208-d230c7020dce.png"
AI_ID=2
AI_USERNAME="ai"
AI_FIRST_NAME="The"
AI_LAST_NAME="AI Opponent"
AI_AVATAR="670eb5bf-72cb-45bc-b17c-9fcf029b9197.png"
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
	psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "INSERT INTO barelyaschema.user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, avatar_path) VALUES \
		($OVERLORDS_ID, 'hashed_password_1', '2000-01-01 00:00:00+00', TRUE, '$OVERLORDS_USERNAME', '$OVERLORDS_FIRST_NAME', '$OVERLORDS_LAST_NAME', 'we dont use email', TRUE, TRUE, '2000-01-01 00:00:00+00', '$OVERLORDS_AVATAR'), \
		($AI_ID, 'hashed_password_2', '2000-01-01 00:00:00+00', TRUE, '$AI_USERNAME', '$AI_FIRST_NAME', '$AI_LAST_NAME', 'we dont use email', TRUE, TRUE, '2000-01-01 00:00:00+00', '$AI_AVATAR');"
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

echo -e $GR "Root accounts are correctly set up!" $NC
end_script 0