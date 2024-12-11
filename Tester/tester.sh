#!/bin/bash

# Base URL for the API
BASE_URL="http://127.0.0.1:8000"
TESTS_URL="https://docs.google.com/spreadsheets/d/11uhG7xBOxUAyQIAAKTghT1Bh5gUYxqQ2fPpRNr6fjds/"

# Colors for output
BLUE="\033[0;36m"
GREEN="\e[32m"
RED="\e[31m"
RESET="\e[0m"

# VARS
TOTAL_TESTS=0
TOTAL_TESTS_SUCCESS=0
COLUMN_WIDTH=0

# Files
LOG_FILE="$(dirname "$(realpath "$0")")/results.log"
CSV_FILE="$(dirname "$(realpath "$0")")/testsFromSheets.csv"
RESPONSE_FILE="$(dirname "$(realpath "$0")")/response.json"
ENV_FILE="$(dirname "$(realpath "$0")")/dummy.env"

create_dummy(){
    # First create static dummys to also clean db
    echo -e "${BLUE}Running ./deploy.sh dummy...${RESET}"
    bash "$(dirname "$(realpath "$0")")/../deploy.sh" dummy
    echo -e "${BLUE}Running ./deploy.sh dummy...DONE${RESET}"
    echo -e "${BLUE}Running dummy2.0.sh...${RESET}"
    bash "$(dirname "$(realpath "$0")")/dummy2.0.sh"
    sleep 1
    source $ENV_FILE
    echo -e "${BLUE}Running dummy2.0.sh...${GREEN}done${RESET}"
    # Check if all tokens are there
    if [ -z "$JOHN_ACCESS" ] || [ -z "$ARABELO_ACCESS" ] || [ -z "$ASTEIN_ACCESS" ] || [ -z "$ANSHOVAH_ACCESS" ] || [ -z "$FDAESTR_ACCESS" ] || [ -z "$RPHUYAL_ACCESS" ]; then
        echo -e "${RED}Not all USER_ACCESS vars are set!${RESET}"
        exit 1
    fi
    # Check if all IDs are there
    if [ -z "$JOHN_ID" ] || [ -z "$ARABELO_ID" ] || [ -z "$ASTEIN_ID" ] || [ -z "$ANSHOVAH_ID" ] || [ -z "$FDAESTR_ID" ] || [ -z "$RPHUYAL_ID" ]; then
            echo -e "${RED}Not all USER_ID vars are set!${RESET}"
        exit 1
    fi
    # Check if all usernames are there
    if [ -z "$JOHN_USERNAME" ] || [ -z "$ARABELO_USERNAME" ] || [ -z "$ASTEIN_USERNAME" ] || [ -z "$ANSHOVAH_USERNAME" ] || [ -z "$FDAESTR_USERNAME" ] || [ -z "$RPHUYAL_USERNAME" ]; then
        echo -e "${RED}Not all USER_USERNAME vars are set!${RESET}"
        exit 1
    fi
}

download_tests(){
    # DOWNLOAD
    echo -e "Downloading ${CSV_FILE} from google sheets...\n\t(${TESTS_URL})"
    curl -s -L -o ${CSV_FILE} "${TESTS_URL}export?exportFormat=csv"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to download ${CSV_FILE}${RESET}"
        exit 1
    fi
    # Check if file starts with "<!DOCTYPE html>" then print an error
    first_line=$(head -n 1 ${CSV_FILE})
    if [[ $first_line == "<!DOCTYPE html"* ]]; then
        echo "Failed to download ${CSV_FILE}"
        exit 1
    fi
    echo -e "\n" >> ${CSV_FILE}
    TOTAL_TESTS=$(( $(wc -l < "$CSV_FILE") - 2 ))
    echo "Found ${TOTAL_TESTS} tests in csv file"
    COLUMN_WIDTH=$(awk -F',' 'NR > 1 { if (length($3) > max) max = length($3) } END { print max }' "$CSV_FILE")
    COLUMN_WIDTH=$((COLUMN_WIDTH + 3))
    if [ $COLUMN_WIDTH -lt 20 ]; then
        COLUMN_WIDTH=20
    fi
    echo "Column width for column description: $COLUMN_WIDTH"
}

expand_vars(){
    output_file="/tmp/$(basename $CSV_FILE)"
    variables=("john" "arabelo" "astein" "anshovah" "fdaestr" "rphuyal")
    var_list_access=$(for var in "${variables[@]}"; do echo -n '$'${var^^}'_ACCESS '; done)
    var_list_id=$(for var in "${variables[@]}"; do echo -n '$'${var^^}'_ID '; done)
    for var in "${variables[@]}"; do
        varname="${var^^}_ACCESS"
        export ${var^^}'_ACCESS='${!varname}
        varname="${var^^}_ID"
        export ${var^^}'_ID='${!varname}
    done
    envsubst "$var_list_access" < "$CSV_FILE" > "$output_file"
    mv $output_file $CSV_FILE
    envsubst "$var_list_id" < "$CSV_FILE" > "$output_file"
    mv $output_file $CSV_FILE
}

print_logs(){
    cmd=("$@")
    {
        echo -e "############################################################################################################################"
        echo -e " ~~~ TEST ~~~"
        echo -e " cmd:   ${cmd[*]}"
        echo -e " ~~~ RESPONSE ~~~"
        cat ${RESPONSE_FILE}
        echo -e "\n############################################################################################################################\n"
    } >> "$LOG_FILE"
}

print_padding(){
    local text=$1
    # echo COLUMN_WIDTH: $COLUMN_WIDTH
    local padding_width=$COLUMN_WIDTH
    # echo padding_width: $padding_width
    padding_width=$((padding_width - ${#text}))
    # echo padding_width: $padding_width
    # echo "padding_width: $padding_width" and text: $text and text width: ${#text}
    local padding=$(printf '%*s' "$padding_width" '')
    echo -en "$text$padding"
}

run_tests(){
    echo "cleaning logs..."
    echo "" > $LOG_FILE
    echo "$(date '+%Y-%m-%dT%H:%M:%S')" > $LOG_FILE
    echo "--------------------------------------------" >> $LOG_FILE

    echo "Running tests..."
    echo "========================================================================================================"
    echo -en "${BLUE}TEST\t+/-  "
    print_padding "DESCRIPTION"
    echo -e "RESPONSE  TYPE    MESSAGE${RESET}"
    echo "========================================================================================================"

    # Read the CSV file line by line
    skip_first_line=true
    while IFS=',' read -r should_work expected short_description user method endpoint args; do
        # Skip the first line
        if $skip_first_line; then
            skip_first_line=false
            continue
        fi

        if [[ -z "$should_work" ]]; then
            continue
        fi
        
        # If args are empty, set payload to empty JSON
        if [[ -z "$args" ]]; then
            args="{}"
        else
            # Never touch this again! It's working!
            args=$(echo "$args" | sed -e 's/,[^,]*$//')
            args=$(echo "$args" | sed -e 's/^"//' -e 's/"$//' -e 's/""/"/g')
        fi

        if [[ "$user" == "NONE" ]]; then
            # Curl with no token
            cmd=(curl -s -k -o ${RESPONSE_FILE} -w "%{http_code}" -X $method "$BASE_URL$endpoint" \
              -H "Content-Type: application/json" \
              -d "$args")
        else
            # Curl with token
            cmd=(curl -s -k -o ${RESPONSE_FILE} -w "%{http_code}" -X $method "$BASE_URL$endpoint" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $user" \
                -d "$args")
        fi

        # Run the curl command
        HTTP_CODE=$("${cmd[@]}")
        print_logs "${cmd[@]}"

        # Format the output
        if [[ "$HTTP_CODE" == "$expected" ]]; then
            echo -en "${GREEN} ok${RESET}\t"
            ((TOTAL_TESTS_SUCCESS++))
        else
            echo -en "${RED} ko${RESET}\t"
        fi
        if [[ $should_work == "+" ]]; then
            echo -en "${GREEN} +   ${RESET}"
        else
            echo -en "${RED} -   ${RESET}"
        fi
        print_padding "$short_description"
        if [[ "$HTTP_CODE" == "$expected" ]]; then
            echo -en "${GREEN}$HTTP_CODE${RESET}"
        else
            echo -en "${RED}$HTTP_CODE${RESET}"
        fi
        echo -en "/${GREEN}$expected${RESET}"
        echo -en "   "
        # Parse the response JSON for "message"
        status=$(jq -r '.status // empty' ${RESPONSE_FILE} 2>/dev/null) || status=""
        message=$(jq -r '.message // empty' ${RESPONSE_FILE} 2>/dev/null) || message=""
        if [[ "$status" == "error" ]]; then
            echo -en "${RED}error   ${RESET}"
        elif [[ "$status" == "success" ]]; then
            echo -en "${GREEN}success ${RESET}"
        else
            echo -en "${RED}???     ${RESET}"
        fi
        if [[ -n "$message" ]]; then
            echo -en "$message\n"
        else
            echo -en "${RED}<message key is missing!>${RESET}\n"
        fi

#            printf "${GREEN}%s${RESET}" "$HTTP_CODE"
#        else
#            printf "${RED}expected/is %s/%s${RESET}" "$expected" "$HTTP_CODE"
#            print_logs "${cmd[@]}"
#        fi
        # run_curl "${cmd[@]}"
    done < "$CSV_FILE"


        # Print or process the test case
        # echo "Running Test:"
        # echo "Should Work: $should_work"
        # echo "Expected: $expected"
        # echo "Description: $short_description"
        # echo "User: $user"
        # echo "Method: $method"
        # echo "Endpoint: $endpoint"
        # echo "Args: $clean_args"

        # Example: Mock a request using curl (if this were an HTTP API)
        #if [[ $method == "POST" ]]; then
        #    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -d "$clean_args" "http://localhost$endpoint")
        #    echo "Received Response Code: $response"
        #    if [[ $response -eq $expected ]]; then
        #        echo "Test Passed!"
        #    else
        #        echo "Test Failed!"
        #    fi
        #fi
        #echo "----------------------------"
}

print_summary(){
    success_rate=0
    if [ $TOTAL_TESTS -eq 0 ]; then
        success_rate=0
    else
        if [ "$TOTAL_TESTS_SUCCESS" -eq "$TOTAL_TESTS" ]; then
            echo -e "\n========================================================================================================"
            echo -e "${GREEN} All tests passed!${RESET}"
            echo -e "========================================================================================================"
        else
            echo -e "\n========================================================================================================"
            echo -e "${RED} Some tests failed. See '$LOG_FILE' for details.${RESET}"
            echo -e "========================================================================================================"
        fi
    fi
    success_rate=$(($TOTAL_TESTS_SUCCESS * 100 / $TOTAL_TESTS))
    echo " ${TOTAL_TESTS_SUCCESS}/${TOTAL_TESTS} (${success_rate} % success)"
    echo -e "\n"
}

# MAIN SCRIPT LOGIC
create_dummy
download_tests
expand_vars
run_tests
print_summary