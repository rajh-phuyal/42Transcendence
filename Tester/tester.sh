#!/bin/bash

# Base URL for the API
BASE_URL="https://localhost/api"
TESTS_URL="https://docs.google.com/spreadsheets/d/11uhG7xBOxUAyQIAAKTghT1Bh5gUYxqQ2fPpRNr6fjds/"

# Colors for output
BLUE="\033[0;36m"
GREEN="\033[0;32m"
RED="\033[0;31m"
ORANGE="\033[38;5;214m"
BOLD="\033[1m"
RESET="\033[0m"

# VARS
TOTAL_TESTS=0
TOTAL_TESTS_SUCCESS=0
FAILED_TESTS=""
TEST_TO_PERFORM=""
UPPER_TEST_RANGE=""

# Files
LOG_FILE="$(dirname "$(realpath "$0")")/results.log"
CSV_FILE="$(dirname "$(realpath "$0")")/testsFromSheets.csv"
RESPONSE_FILE="$(dirname "$(realpath "$0")")/response.json"
ENV_FILE="$(dirname "$(realpath "$0")")/dummy.env"
LIVE_DUMMY_FILE="$(dirname "$(realpath "$0")")/live_dummy.sh"

# To be able to print in color to the terminal and in plain text to the log file
print_and_log() {
    local newline=true
    local color=""
    local text=""

    # Parse options
    while [[ "$1" =~ ^- ]]; do
        case $1 in
            -n) newline=false ;; # No newline
            *) break ;;
        esac
        shift
    done

    # Extract color and text
    color="$1"
    text="$2"

    # Print to terminal with color
    if [[ $newline == true ]]; then
        echo -e "${color}${text}${RESET}"
    else
        echo -en "${color}${text}${RESET}"
    fi

    # Write plain text to log file (without color)
    if [[ $newline == true ]]; then
        echo -e "${text}" >> "$LOG_FILE"
    else
        echo -en "${text}" >> "$LOG_FILE"
    fi
}

check_for_envs(){
    source ${ENV_FILE}
    # Check if all tokens are there
    if [ -z "$JOHN_ACCESS" ] || [ -z "$ARABELO_ACCESS" ] || [ -z "$ASTEIN_ACCESS" ] || [ -z "$ANSHOVAH_ACCESS" ] || [ -z "$FDAESTR_ACCESS" ] || [ -z "$RPHUYAL_ACCESS" ]; then
        echo -e "${RED}Not all USER_ACCESS vars are set!${RESET}"
        echo -e "${ORANGE}Rerun this script and allow the dummy data to be created${RESET}"
        exit 1
    fi
    # Check if all IDs are there
    if [ -z "$JOHN_ID" ] || [ -z "$ARABELO_ID" ] || [ -z "$ASTEIN_ID" ] || [ -z "$ANSHOVAH_ID" ] || [ -z "$FDAESTR_ID" ] || [ -z "$RPHUYAL_ID" ]; then
            echo -e "${RED}Not all USER_ID vars are set!${RESET}"
            echo -e "${ORANGE}Rerun this script and allow the dummy data to be created${RESET}"
        exit 1
    fi
    # Check if all usernames are there
    if [ -z "$JOHN_USERNAME" ] || [ -z "$ARABELO_USERNAME" ] || [ -z "$ASTEIN_USERNAME" ] || [ -z "$ANSHOVAH_USERNAME" ] || [ -z "$FDAESTR_USERNAME" ] || [ -z "$RPHUYAL_USERNAME" ]; then
        echo -e "${RED}Not all USER_USERNAME vars are set!${RESET}"
        echo -e "${ORANGE}Rerun this script and allow the dummy data to be created${RESET}"
        exit 1
    fi
}


create_dummy(){
    # Ask to create dummy users
    echo -e "${ORANGE}U need dummy data for the tests to work!${RESET}"
    echo -e "${ORANGE}If u have created them with a previous run, just press enter${RESET}"
    read -p "Wanna create dummy data? Input y: " input
    if [[ -z "$input" ]]; then
        return
    fi
    # First create static dummys to also clean db
    echo -e "${BLUE}Running ./deploy.sh dummy...${RESET}"
    bash "$(dirname "$(realpath "$0")")/../deploy.sh" dummy
    echo -e "${BLUE}Running ./deploy.sh dummy...DONE${RESET}"
    echo -e "${BLUE}Running dummy2.0.sh...${RESET}"
    bash "$(dirname "$(realpath "$0")")/dummy2.0.sh"
    sleep 1
    source $ENV_FILE
    echo -e "${BLUE}Running dummy2.0.sh...${GREEN}done${RESET}"
    bash "$LIVE_DUMMY_FILE"
    check_for_envs
}

download_tests(){
    TOTAL_TESTS=$(( $(awk 'length($0) > 20' "$CSV_FILE" | wc -l)))
    TOTAL_TESTS=$(printf "%03d" "$TOTAL_TESTS")
    if [[ $TOTAL_TESTS -ne -2 ]]; then
        echo -e "${BLUE}Found ${TOTAL_TESTS} tests in csv file${RESET}"
        # Ask to download tests
        echo -e "${ORANGE}If u don't wanna update/download them again, just press enter${RESET}"
        read -p "Wanna download/update tests? Input y: " input
        if [[ -z "$input" ]]; then
            return
        fi
    fi

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
    TOTAL_TESTS=$(( $(awk 'length($0) > 20' "$CSV_FILE" | wc -l)))
    TOTAL_TESTS=$(printf "%03d" "$TOTAL_TESTS")
    echo -e "${BLUE}Found ${TOTAL_TESTS} tests in csv file${RESET}"
}

expand_vars(){
    check_for_envs
    output_file="/tmp/$(basename $CSV_FILE)"
    variables=("john" "arabelo" "astein" "anshovah" "fdaestr" "rphuyal")
    var_list_access=$(for var in "${variables[@]}"; do echo -n '$'$(echo "$var" | tr '[:lower:]' '[:upper:]')'_ACCESS '; done)
    var_list_id=$(for var in "${variables[@]}"; do echo -n '$'$(echo "$var" | tr '[:lower:]' '[:upper:]')'_ID '; done)
    var_list_username=$(for var in "${variables[@]}"; do echo -n '$'$(echo "$var" | tr '[:lower:]' '[:upper:]')'_USERNAME '; done)

    for var in "${variables[@]}"; do
        var_upper=$(echo "$var" | tr '[:lower:]' '[:upper:]')
        varname="${var_upper}_ACCESS"
        export ${var_upper}_ACCESS="${!varname}"
        varname="${var_upper}_ID"
        export ${var_upper}_ID="${!varname}"
        varname="${var_upper}_USERNAME"
        export ${var_upper}_USERNAME="${!varname}"
    done

    envsubst "$var_list_access" < "$CSV_FILE" > "$output_file"
    mv $output_file $CSV_FILE
    envsubst "$var_list_id" < "$CSV_FILE" > "$output_file"
    mv $output_file $CSV_FILE
    envsubst "$var_list_username" < "$CSV_FILE" > "$output_file"
    mv $output_file $CSV_FILE
}

# ask for a specific test number; if empty runn all tests
select_test(){
    echo "cleaning logs..."
    echo "" > $LOG_FILE
    echo "$(date '+%Y-%m-%dT%H:%M:%S')" > $LOG_FILE
    echo "--------------------------------------------" >> $LOG_FILE

    echo -e "Enter test number\n\t${BOLD}return${RESET}\tfor all tests\n\t${BOLD}42${RESET}\tonly test with number: 42\n\t${BOLD}-42${RESET}\tfor range 1-42"
    read -p "choose: " INPUT

    local total_tests_num=$((10#$TOTAL_TESTS))
    if [[ -n "$INPUT" ]]; then
        if [[ $INPUT == -* ]]; then
            UPPER_TEST_RANGE=${INPUT:1}
            # UPPER_TEST_RANGE=$(printf "%03d" "$UPPER_TEST_RANGE")
            if [[ $UPPER_TEST_RANGE -gt $total_tests_num ]]; then
                print_and_log "" "Test number $UPPER_TEST_RANGE does not exist"
                print_and_log "" "Ignoring range aka running all tests"
                UPPER_TEST_RANGE=""
                return
            fi
            print_and_log "" "Running tests 001-$UPPER_TEST_RANGE"
            return
        fi
        TEST_TO_PERFORM=$INPUT
        if [[ $TEST_TO_PERFORM -gt $total_tests_num ]]; then
            echo "Test number $TEST_TO_PERFORM does not exist"
            exit 1
        fi
        print_and_log "" "Running test $TEST_TO_PERFORM"
    else
        print_and_log "" "Running all tests"
    fi
}

print_test_header(){
    # Get the vars
    if [ $# -lt 9 ]; then
        echo "Error: Insufficient arguments for print_test_header. Expected at least 9 arguments."
        exit 1
    fi
    local test_number=${1}
    local should_work=${2}
    local expected=${3}
    local keys=${4}
    local short_description=${5}
    local user=${6}
    local method=${7}
    local endpoint=${8}
    local args=${9}

    if [[ -z "$endpoint" ]]; then
        endpoint="none"
    fi
    if [[ -z "$keys" ]]; then
        keys="none"
    fi

    # Print the test header to console and log file
    print_and_log "" "\n========================================================================================================"
    print_and_log "${BLUE}" "TEST NO: ${test_number}"
    print_and_log "" "=================="
    print_and_log "" "short description:\t${short_description}"
    print_and_log "" "method:\t\t\t$method"
    print_and_log "" "endpoint:\t\t$endpoint"
    print_and_log "" "user:\t\t\t${user:0:77}$( [ ${#user} -gt 77 ] && echo '...' )"
    print_and_log "" "args:\t\t\t$args"
    print_and_log -n "" "should work?:\t\t"
    if [[ $should_work == "+" ]]; then
        print_and_log "${GREEN}" "+"
    else
        print_and_log "${RED}" "-"
    fi
    print_and_log "" "expected response code:\t$expected"
    print_and_log "" "expected response keys:\t$keys"
    print_and_log "" "========================================================================================================"
}

# Runs single test
# - Prints the test to the console
# - Runs the curl command
# - Updates the console output
# - Check the resonse
# - Updates the log file
# - Clears the console output
run_test() {
    ((TOTAL_TESTS++))
    # Get the vars
    if [ $# -lt 9 ]; then
        print_and_log "" "Error: Insufficient arguments for run_test. Expected at least 9 arguments."
        exit 1
    fi
    local test_number=${1}
    local should_work=${2}
    local expected=${3}
    local keys=${4}
    local short_description=${5}
    local user=${6}
    local method=${7}
    local endpoint=${8}
    local args=${9}

    echo -e "\n========================================================================================================" >> "$LOG_FILE"
    print_and_log "-n" "${BOLD}" "   ${test_number}:\t"
    print_and_log "-n" "${BLUE}" "expected:\t"
    print_and_log "${expected} ${keys} "
    echo -e "========================================================================================================" >> "$LOG_FILE"
    echo -e "   ---" >> "$LOG_FILE"
    if [[ "$user" == "NONE" ]]; then
        # Curl with no token
        cmd=(curl -s -k -o ${RESPONSE_FILE} -w "%{http_code}" -X $method "$BASE_URL$endpoint" \
          -H "Content-Type: application/json" \
          -d "$args")
    else
        # Curl with token
        cmd=(curl -s -k -o ${RESPONSE_FILE} -w "%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            --cookie "access_token=$user" \
            -d "$args")
    fi
    # Remove old response file
    rm -f ${RESPONSE_FILE} | true
    # Run the curl command
    HTTP_CODE=$("${cmd[@]}")
    echo -e "   cmd: ${cmd[@]}" >> "$LOG_FILE"
    echo -e "   ---" >> "$LOG_FILE"

    # Validate the response
    local test_successfull=true
    echo -n "      response code (expected/got): $expected/" >> "$LOG_FILE"
    echo "$HTTP_CODE" >> "$LOG_FILE"
    echo -en "${BLUE}\t\t\tresult:\t\t${RESET}"
    if [[ "$HTTP_CODE" != "$expected" ]]; then
        echo -en "${RED}${HTTP_CODE} ${RESET}"
        test_successfull=false
    else
        echo -en "${GREEN}${HTTP_CODE} ${RESET}"
    fi

    # Check if the response is an html
    if [[ $(file -b --mime-type ${RESPONSE_FILE}) == "text/html" ]]; then
        echo -en "${RED}(received an HTML response instead of JSON)${RESET}"
        echo ">>> html file: bla bla bla (to lazy to log the full file <<<)" > ${RESPONSE_FILE}
        test_successfull=false
    else
        # Check if the response JSON is valid
        local message=""
        echo "      expected keys:" >> "$LOG_FILE"
        for key in $keys; do
            echo -ne "         $key:\t" >> "$LOG_FILE"
            key_exists=$(jq -r "has(\"$key\")" ${RESPONSE_FILE})
            if [[ "$key_exists" == "true" ]]; then
                # Key exists
                value=$(jq -r ".$key" ${RESPONSE_FILE})
                if [[ $key == "status" ]]; then
                    if [[ "$should_work" == "+" ]]; then
                        if [[ "$value" == "success" ]]; then
                            echo -en "${GREEN}$key ${RESET}"
                            echo "$value"  >> "$LOG_FILE"
                        else
                            echo -en "${ORANGE}$key ${RESET}"
                            echo "$value (expected 'success' !!!)" >> "$LOG_FILE"
                            test_successfull=false
                        fi
                    else
                        if [[ "$value" == "error" ]]; then
                            echo -en "${GREEN}$key ${RESET}"
                            echo "$value"  >> "$LOG_FILE"
                        else
                            echo -en "${ORANGE}$key ${RESET}"
                            echo "$value (expected 'error' !!!)"  >> "$LOG_FILE"
                            test_successfull=false
                        fi
                    fi
                    continue
                fi
                echo "$value"  >> "$LOG_FILE"
                echo -en "${GREEN}$key ${RESET}"
                if [[ $key == "message" ]]; then
                    message="($value)"
                fi
            else
                echo "<expected key '$key' is missing!>"  >> "$LOG_FILE"
                echo -en "${RED}$key ${RESET}"
                test_successfull=false
            fi
        done
    fi
    echo "   ---"  >> "$LOG_FILE"
    echo -n "   result: "  >> "$LOG_FILE"
    if [[ $test_successfull == true ]]; then
        echo "ok"  >> "$LOG_FILE"
        local message_short=$message
        if [[ ${#message_short} -gt 37 ]]; then
            message_short="${message_short:0:$((34))}...)"
        fi
        echo -e " | ${GREEN}ok${RESET} $message_short\n"
        ((TOTAL_TESTS_SUCCESS++))
    else
        FAILED_TESTS="$FAILED_TESTS\n$test_number"
        echo "ko"  >> "$LOG_FILE"
        echo -e " | ${RED}ko${RESET} $message\n"
    fi

    # Log the response file and delete it
    echo -e " ---" >> "$LOG_FILE"
    echo -e " response:" >> "$LOG_FILE"
    echo -e " ---" >> "$LOG_FILE"
    (cat "${RESPONSE_FILE}" 2>/dev/null || echo "<No response file found>") >> "$LOG_FILE"
    rm -f ${RESPONSE_FILE} | true
}

# This creates multiple tests for one line
# - The line itself
# - The line with the other 3 request types
# - If the line needs a token
#     -> try without token
#     -> try with wrong token
# - If the line needs arguments
#     -> try withouth arguments
run_tests(){
    # Get the vars
    if [ $# -lt 9 ]; then
        echo "Error: Insufficient arguments for run_tests. Expected at least 9 arguments."
        exit 1
    fi
    local test_number="${1}"
    local should_work="${2}"
    local expected="${3}"
    local keys="${4}"
    local short_description="${5}"
    local user="${6}"
    local method="${7}"
    local endpoint="${8}"
    local args="${9}"
    # Add status and message as a required key
    if [[ -z "$keys" ]]; then
        keys="status message"
    else
        keys="status message $keys"
    fi

    print_test_header "$test_number" "$should_work" "$expected" "$keys" "$short_description" "$user" "$method" "$endpoint" "$args"

    # A: The line itself
    test_number_new="${test_number} A  (original)"
    run_test "$test_number_new" "$should_work" "$expected" "$keys" "$short_description" "$user" "$method" "$endpoint" "$args"

    basic_keys="status message"

    # B: The line with the other 3 request types
    methods=("POST" "GET" "PUT" "DELETE")
    test_sub_number=1
    for other_method in "${methods[@]}"; do
        if [[ "$other_method" == "$method" ]]; then
            continue
        fi
        test_number_new="${test_number} B$test_sub_number ($other_method)"
        run_test "$test_number_new" "-" "405" "$basic_keys" "$short_description" "$user" "$other_method" "$endpoint" "$args"
        test_sub_number=$((test_sub_number + 1))
    done

#TODO: UNCOMMENT THIS WHEN CODE ON MAIN IS FIXED @rajh
    # C: If the line needs a token
#    if [[ "$user" != "NONE" ]]; then
#        # C1: try without token
#        test_number_new="${test_number} C1 (no token)"
#        run_test "$test_number_new" "-" "401" "$basic_keys" "$short_description" "NONE" "$method" "$endpoint" "$args"
#
#        # C2: try with wrong token
#        test_number_new="${test_number} C2 (wrong tok.)"
#        run_test "$test_number_new" "-" "401" "$basic_keys" "$short_description" "thisIsAWrongToken" "$method" "$endpoint" "$args"
#    fi

    # D: If the line needs arguments
    if [[ -n "$args" ]]; then
        # D1: try withouth arguments
        test_number_new="${test_number} D1 (no args)"
        run_test "$test_number_new" "-" "400" "$basic_keys" "$short_description" "$user" "$method" "$endpoint" "{}"
    fi

    print_and_log "" "========================================================================================================\n"
}

# This loops trough the CSV file and creates tests for each line
parse_lines(){
    # Reset total tests since we generate more tests than lines
    TOTAL_TESTS=0
    SKIPPED_TESTS=""
    echo "Let's go..."
    echo "========================================================================================================"

    # Read the CSV file line by line
    local test_no=0
    while IFS=',' read -r active should_work expected keys short_description user method endpoint args; do
        test_no=$((test_no + 1))
        local test_number=$(printf "%03d" "$test_no")
        test_num=$((10#$test_number))
        # Skip the first line
        if [[ "$test_no" == "1" ]]; then
            continue
        fi

        # Check if test number is there and active (aka no empty line)
        if [[ -z "$test_number" || -z "$active" ]]; then
            continue
        fi

        # Check if only one test should be run
        if [[ -n "$TEST_TO_PERFORM" ]] && [[ "$test_num" != "$TEST_TO_PERFORM" ]]; then
            continue
        fi

        # Check if only a range of tests should be run
        if [[ -n "$UPPER_TEST_RANGE" ]] && [[ "$test_num" -gt "$UPPER_TEST_RANGE" ]]; then
            break
        fi

        # Check if test is marekd as active
        if [[ "$active" != "x" ]]; then
            if [[ "$should_work" != "" ]]; then
                SKIPPED_TESTS="$SKIPPED_TESTS $test_number"
            fi
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

        run_tests "$test_number" "$should_work" "$expected" "$keys" "$short_description" "$user" "$method" "$endpoint" "$args"
    done < "$CSV_FILE"
    if [[ -n "$SKIPPED_TESTS" ]]; then
        print_and_log "${RED}" "The following tests were skipped because they are not marked as active in the sheet:"
        print_and_log "${RED}" "======="
        print_and_log "${RED}" "Skipped tests: $SKIPPED_TESTS"
        print_and_log "${RED}" "======="
    fi
    if [[ -n "$FAILED_TESTS" ]]; then
        print_and_log "" "\n"
        print_and_log "${RED}" "The following tests failed:"
        print_and_log -n "${RED}" "======="
        print_and_log "${RED}" "$FAILED_TESTS"
        print_and_log "${RED}" "======="
    fi
}

print_summary(){
    success_rate=0
    if [ $TOTAL_TESTS -eq 0 ]; then
        success_rate=0
    else
        success_rate=$((${TOTAL_TESTS_SUCCESS} * 100 / ${TOTAL_TESTS}))
    fi
    if [ "$TOTAL_TESTS_SUCCESS" -eq "$TOTAL_TESTS" ]; then
        print_and_log "" "\n========================================================================================================"
        print_and_log "${GREEN}" " All tests passed!"
        print_and_log "" "========================================================================================================"
    else
        print_and_log "" "\n========================================================================================================"
        print_and_log "${RED}" " Some tests failed. See '$LOG_FILE' for details."
        print_and_log "" "========================================================================================================"
    fi
    print_and_log "" " ${TOTAL_TESTS_SUCCESS}/${TOTAL_TESTS} (${success_rate} % success)"
    print_and_log "" "\n"
}

# MAIN SCRIPT LOGIC
create_dummy
download_tests
expand_vars
select_test
parse_lines
print_summary