#!/bin/bash

# Define the base URL for the API
BASE_URL="https://localhost/api"
ENV_FILE="$(dirname "$(realpath "$0")")/dummy.env"
RESPONSE_FILE="$(dirname "$(realpath "$0")")/response.json"

# Define the endpoint for registration
REGISTER_ENDPOINT="/auth/register/"
USER_UPDATE_INFO="/user/update-user-info/"
RELATIONSHIP_ENDPOINT="/user/relationship/"
CREATE_CHAT_ENDPOINT="/chat/create/conversation/"
CREATE_GAME_ENDPOINT="/game/create/"

# Define the password to use for all users
PASSWORD="BarelyAPassword123!!!"

# Array of usernames to register
USERNAMES=(
    "john"
    "arabelo"
    "astein"
    "anshovah"
    "fdaestr"
    "rphuyal"
)

# Colors for output
GREEN="\033[0;32m"
RED="\033[0;31m"
RESET="\033[0m"

# Function to register a user and export tokens
register_user() {
    local base_username=$1
    local username=$base_username
    local payload="{\"username\": \"$username\", \"password\": \"$PASSWORD\"}"
    local attempt=1
    local output="Registering user: "

    while true; do
        HTTP_CODE=$(curl -s -k -o ${RESPONSE_FILE} -w "%{http_code}" -X POST "$BASE_URL$REGISTER_ENDPOINT" \
            -H "Content-Type: application/json" \
            -d "$payload" \
            -c temp_cookie.txt)

        if [ "$HTTP_CODE" -eq 200 ]; then
            # Parse JSON response and export variables
            USER_ID=$(jq -r '.userId' ${RESPONSE_FILE})
            ACCESS_TOKEN=$(awk '/access_token/ {print $NF}' temp_cookie.txt)
            REFRESH_TOKEN=$(awk '/refresh_token/ {print $NF}' temp_cookie.txt)
            USER_NAME=$(jq -r '.username' ${RESPONSE_FILE})
            output+="${GREEN}$username${RESET}\t($PASSWORD)\t(id: $USER_ID)"
            echo -e "$output"
            # Export variables with the original base username prefix
            export $(echo "${base_username}_ID" | tr '[:lower:]' '[:upper:]')="$USER_ID"
            export $(echo "${base_username}_ACCESS" | tr '[:lower:]' '[:upper:]')="$ACCESS_TOKEN"
            export $(echo "${base_username}_REFRESH" | tr '[:lower:]' '[:upper:]')="$REFRESH_TOKEN"
            export $(echo "${base_username}_USERNAME" | tr '[:lower:]' '[:upper:]')="$USER_NAME"
            echo "$(echo "${base_username}_ID" | tr '[:lower:]' '[:upper:]')=$USER_ID" >> ${ENV_FILE}
            echo "$(echo "${base_username}_ACCESS" | tr '[:lower:]' '[:upper:]')=$ACCESS_TOKEN" >> ${ENV_FILE}
            echo "$(echo "${base_username}_REFRESH" | tr '[:lower:]' '[:upper:]')=$REFRESH_TOKEN" >> ${ENV_FILE}
            echo "$(echo "${base_username}_USERNAME" | tr '[:lower:]' '[:upper:]')=$USER_NAME" >> ${ENV_FILE}
            break
        else
            # Check if username already exists and try a new one
            if grep -q "Username .* already exists" ${RESPONSE_FILE}; then
                output+="${RED}$username${RESET} "
                attempt=$((attempt + 1))
                username="${base_username}${attempt}"
                payload="{\"username\": \"$username\", \"password\": \"$PASSWORD\"}"
            else
                echo "Failed to register user $username. HTTP Code: $HTTP_CODE"
                cat ${RESPONSE_FILE}
                break
            fi
        fi
    done
    rm temp_cookie.txt
}

update_user_details(){
    local sender=$1
    local first_name=$2
    local last_name=$3
    local language=$4

    local access_token_var="$(echo "${sender}_ACCESS" | tr '[:lower:]' '[:upper:]')"
    local access_token=${!access_token_var}
    local username_var="$(echo "${sender}_USERNAME" | tr '[:lower:]' '[:upper:]')"
    local username=${!username_var}
    local payload="{\"username\": \"$username\", \"firstName\": \"$first_name\", \"lastName\": \"$last_name\", \"language\": \"$language\"}"

    HTTP_CODE=$(curl -s -k -o ${RESPONSE_FILE} -w "%{http_code}" -X PUT "$BASE_URL$USER_UPDATE_INFO" \
        -H "Content-Type: application/json" \
        --cookie "access_token=$access_token" \
        -d "$payload")

    if [ "$HTTP_CODE" -eq 200 ]; then
        echo -e "Updating user details for $sender: ${GREEN}ok${RESET}"
    else
        echo -e "Updating user details for $sender: ${RED}ko${RESET}"
    fi
}

# Function to send a friend request
send_friend_request() {
    local sender=$1
    local target_username=$2

    local access_token_var="$(echo "${sender}_ACCESS" | tr '[:lower:]' '[:upper:]')"
    local access_token=${!access_token_var}
    local target_id_var="$(echo "${target_username}_ID" | tr '[:lower:]' '[:upper:]')"
    local target_id=${!target_id_var}

    HTTP_CODE=$(curl -s -k -o ${RESPONSE_FILE} -w "%{http_code}" -X POST "$BASE_URL$RELATIONSHIP_ENDPOINT/send/$target_id/" \
        -H "Content-Type: application/json" \
        --cookie "access_token=$access_token")
    if [ "$HTTP_CODE" -eq 201 ]; then
        echo -e "Sending friend request from $sender to $target_username: ${GREEN}ok${RESET}"
    else
        echo -e "Sending friend request from $sender to $target_username: ${RED}ko${RESET}"
    fi
}

# Function to accept a friend request
accept_friend_request() {
    local receiver=$1
    local sender_username=$2

    local access_token_var="$(echo "${receiver}_ACCESS" | tr '[:lower:]' '[:upper:]')"
    local access_token=${!access_token_var}
    local sender_id_var="$(echo "${sender_username}_ID" | tr '[:lower:]' '[:upper:]')"
    local sender_id=${!sender_id_var}

    HTTP_CODE=$(curl -s -k -o ${RESPONSE_FILE} -w "%{http_code}" -X PUT "$BASE_URL$RELATIONSHIP_ENDPOINT/accept/$sender_id/" \
        -H "Content-Type: application/json" \
        --cookie "access_token=$access_token")
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo -e "Accepting friend request from $sender_username to $receiver: ${GREEN}ok${RESET}"
    else
        echo -e "Accepting friend request from $sender_username to $receiver: ${RED}ko${RESET}"
    fi
}

# Function to block a user
block_user() {
    local blocker=$1
    local target_username=$2

    local access_token_var="$(echo "${blocker}_ACCESS" | tr '[:lower:]' '[:upper:]')"
    local access_token=${!access_token_var}
    local target_id_var="$(echo "${target_username}_ID" | tr '[:lower:]' '[:upper:]')"
    local target_id=${!target_id_var}

    HTTP_CODE=$(curl -s -k -o ${RESPONSE_FILE} -w "%{http_code}" -X POST "$BASE_URL$RELATIONSHIP_ENDPOINT/block/$target_id/" \
        -H "Content-Type: application/json" \
        --cookie "access_token=$access_token")
    if [ "$HTTP_CODE" -eq 201 ]; then
        echo -e "Blocking user $target_username by $blocker: ${GREEN}ok${RESET}"
    else
        echo -e "Blocking user $target_username by $blocker: ${RED}ko${RESET}"
    fi
}

# Function to create a chat conversation
create_chat() {
    local sender=$1
    local target_username=$2
    local message=$3

    local access_token_var="$(echo "${sender}_ACCESS" | tr '[:lower:]' '[:upper:]')"
    local access_token=${!access_token_var}
    local target_id_var="$(echo "${target_username}_ID" | tr '[:lower:]' '[:upper:]')"
    local target_id=${!target_id_var}

    local payload="{\"userId\": $target_id, \"initialMessage\": \"$message\"}"

    HTTP_CODE=$(curl -s -k -o ${RESPONSE_FILE} -w "%{http_code}" -X POST "$BASE_URL$CREATE_CHAT_ENDPOINT" \
        -H "Content-Type: application/json" \
        --cookie "access_token=$access_token" \
        -d "$payload")

    if [ "$HTTP_CODE" -eq 200 ]; then
        echo -e "Creating chat from $sender to $target_username: ${GREEN}ok${RESET}"
    else
        echo -e "Creating chat from $sender to $target_username: ${RED}ko${RESET}"
    fi
}

# Function to create a game
create_game() {
    local creator=$1
    local opponent=$2
    local map_number=$3
    local powerups=$4

    local access_token_var="$(echo "${creator}_ACCESS" | tr '[:lower:]' '[:upper:]')"
    local access_token=${!access_token_var}
    local opponent_id_var="$(echo "${opponent}_ID" | tr '[:lower:]' '[:upper:]')"
    local opponent_id=${!opponent_id_var}

    local payload="{\"mapNumber\": $map_number, \"powerups\": \"$powerups\", \"opponentId\": $opponent_id}"

    HTTP_CODE=$(curl -s -k -o ${RESPONSE_FILE} -w "%{http_code}" -X POST "$BASE_URL$CREATE_GAME_ENDPOINT" \
        -H "Content-Type: application/json" \
        --cookie "access_token=$access_token" \
        -d "$payload")

    if [ "$HTTP_CODE" -eq 200 ]; then
        echo -e "Creating game from $creator to $opponent: ${GREEN}ok${RESET}"
    else
        echo -e "Creating game from $creator to $opponent: ${RED}ko${RESET}"
    fi
}

# Additional debugging step to verify endpoint accessibility
check_endpoint() {
    echo "Checking endpoint accessibility..."
    curl -s -k -X GET "$BASE_URL$REGISTER_ENDPOINT" > /dev/null && echo "Endpoint is accessible." || echo "Endpoint is not accessible."
}

# Ensure the script is not running in a container
if grep -q "/docker/" /proc/1/cgroup; then
    echo "This script should not be run inside a Docker container."
    exit 1
fi

# Debug endpoint first
check_endpoint

# Creating empty ${ENV_FILE}
echo "" > ${ENV_FILE}

# Register each user
for username in "${USERNAMES[@]}"; do
    register_user "$username"
done

# Updating user details
update_user_details "john" "John" "Doe" "en-US"
update_user_details "arabelo" "Alê" "Guedes" "pt-BR"
update_user_details "astein" "Alex" "Stein" "de-DE"
update_user_details "anshovah" "Anatolii" "Shovah" "uk-UA"
update_user_details "fdaestr" "Francisco" "Inácio" "pt-PT"
update_user_details "rphuyal" "Rajh" "Phuyal" "ne-NP"

# Sending example Friend Requests
send_friend_request "arabelo" "astein"
send_friend_request "arabelo" "anshovah"
send_friend_request "arabelo" "fdaestr"
send_friend_request "arabelo" "rphuyal"
send_friend_request "astein" "anshovah"
send_friend_request "astein" "fdaestr"
send_friend_request "rphuyal" "fdaestr"
send_friend_request "rphuyal" "astein"

# Accepting example Friend Requests
accept_friend_request "astein" "arabelo"
accept_friend_request "anshovah" "arabelo"
accept_friend_request "fdaestr" "arabelo"
accept_friend_request "rphuyal" "arabelo"
accept_friend_request "anshovah" "astein"

# Blocking example Users
block_user "anshovah" "fdaestr"
block_user "fdaestr" "anshovah"

# Creating chat conversations
create_chat "arabelo" "astein" "Hi Alex, how are you lol?"
create_chat "arabelo" "fdaestr" "Hi Anatolii, how are you? lol"
exit 1
# Creating games
create_game "astein" "anshovah" 1 true
