#!/bin/bash

# Input file
BASE_URL="http://127.0.0.1:8000"
INPUT_FILE="$(dirname "$(realpath "$0")")/tests.cool"

# Colors for output
BLUE="\e[34m"
GREEN="\e[32m"
RED="\e[31m"
RESET="\e[0m"

# Log file for failed tests
LOG_FILE="barelyA.log"
echo "" > "$LOG_FILE"

# Run the dummy2.0.sh script
echo -e "${BLUE}Running dummy2.0.sh...${RESET}"
# bash "$(dirname "$(realpath "$0")")/dummy2.0.sh" TODO: uncomment this line
sleep 1
source "$(dirname "$(realpath "$0")")/dummy.env"
echo -e "${BLUE}Running dummy2.0.sh...${GREEN}done${RESET}"

echo $ASTEIN_ID

# Start testing
echo -e "${BLUE}Starting tests...${RESET}"

# Ensure BASE_URL and other environment variables are set
if [ -z "$BASE_URL" ]; then
  echo "Error: BASE_URL is not set. Please set the necessary environment variables before running."
  exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: Input file '$INPUT_FILE' not found."
  exit 1
fi

# Find the longest description for formatting
description_width=$(awk -F';' '/^[^#]/ { if (length($2) > max) max = length($2) } END { print max }' "$INPUT_FILE")

# Initialize log file
> "$LOG_FILE"

# Counters for success and total tests
success_count=0
total_count=0

# Process each valid line in the input file
while IFS= read -r line; do
  # Skip comments and empty lines
  if [[ "$line" =~ ^# ]] || [[ -z "$line" ]]; then
    continue
  fi

  # Detect new entry start
  if [[ "$line" == works=* ]]; then
    # Reset variables for a new entry
    mark=""
    description=""
    user=""
    method=""
    endpoint=""
    args=""
    expected_code=""
  fi

  # Extract key-value pairs
  key=$(echo "$line" | cut -d '=' -f 1 )
  value=$(echo "$line" | cut -d '=' -f 2- )

  # Assign to the correct variable based on the key
  case "$key" in
    works) mark="$value" ;;
    description) description="$value" ;;
    user) user="$value" ;;
    method) method="$value" ;;
    endpoint) endpoint="$value" ;;
    args) args="$value" ;;
    expected_code) expected_code="$value" ;;
  esac

  # When all variables are set, process the entry
  if [[ -n "$mark" && -n "$description" && -n "$method" && -n "$endpoint" && -n "$args" && -n "$expected_code" ]]; then
    # Trim leading/trailing whitespace (for safety)
   # mark=$(echo "$mark" | xargs)
   # description=$(echo "$description" | xargs)
   # user=$(echo "$user" | xargs)
   # method=$(echo "$method" | xargs)
   # endpoint=$(echo "$endpoint" | xargs)
   # args=$(echo "$args" | xargs)
   # expected_code=$(echo "$expected_code" | xargs)

    # Expand variables in args
    echo "$args"
    expanded_args=$(printf "%s" "$args" | eval "echo \"$args\"")
    echo "$expanded_args"

    # Increment total tests
    ((total_count++))

    # Output mark and description with alignment
    if [[ "$mark" == "+" ]]; then
      echo -en "${GREEN}  +  ${RESET}"
    else
      echo -en "${RED}  -  ${RESET}"
    fi
    printf "%-${description_width}s" "$description  "
    HTTP_CODE=-42
    username="ahokcooaaaaaaooool"
    password="hello123HELLO!!!"
    payload="{ $expanded_args }"
    if [[ "$user" == "NONE" ]]; then
      # Curl with no token
      cmd=(curl -s -k -o response.json -w "%{http_code}" -X POST "$BASE_URL/auth/register/" \
        -H "Content-Type: application/json" \
        -d "$payload")
    else
      # Curl with token
      access_token_var="${user}_access"
      if [[ -z "${!access_token_var}" ]]; then
          echo -e "${RED}Token for $user is not set or empty.${RESET}"
          continue
      fi
      acess_token="${!access_token_var}"
      cmd=(curl -s -k -o response.json -w "%{http_code}" -X POST "$BASE_URL/auth/register/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $acess_token" \
        -d "$payload")
    fi
    HTTP_CODE=$("${cmd[@]}")

  
  ## Construct and execute the curl command
  #payload="{ $expanded_args }"
  #cmd=(
  #  curl -s -k -o response.json -w "%{http_code}"
  #  -X "$method"
  #  "$BASE_URL$endpoint"
  #  -H "Content-Type: application/json"
  #)
  #if [[ -n "$token_header" ]]; then
  #  cmd+=(-H "$token_header")
  #fi
  #cmd+=(-d "$payload")
  #echo "Executing: ${cmd[@]}"

  #HTTP_CODE=$("${cmd[@]}")

    # Check the HTTP code
    if [[ "$HTTP_CODE" == "$expected_code" ]]; then
      printf "${GREEN}%s${RESET}" "$HTTP_CODE"
      ((success_count++))
    else
      printf "${RED}expected/is %s/%s${RESET}" "$expected_code" "$HTTP_CODE"
  
      # Log the failed test
      {
        echo -e "############################################################################################################################"
        echo -e " ~~~ TEST ~~~"
        echo -e " input: $line \n"
        echo -e " cmd:   ${cmd[@]}"
        echo -e " ~~~ PARSED ~~~"
        echo -e "   mark:\t\t$mark"
        echo -e "   description:\t\t$description"
        echo -e "   user:\t\t$user ($access_token_var)"
        echo -e "   method:\t\t$method"
        echo -e "   endpoint:\t\t$endpoint"
        echo -e "   args:\t\t$expanded_args"
        echo -e "   expected_code:\t$expected_code\n"
        echo -e " ~~~ RESPONSE ~~~"
        cat response.json
        echo -e "############################################################################################################################"
        echo
      } >> "$LOG_FILE"
    fi
  
    # Parse the response JSON for "message"
    message=$(jq -r '.message // empty' response.json 2>/dev/null) || message=""
  
    if [[ -n "$message" ]]; then
      printf "\t%s\n" "$message"
    else
      printf "\t${RED}<message key is missing!>${RESET}\n"
    fi
  fi

done < "$INPUT_FILE"

# Calculate and print the summary
if [ $success_count -eq $total_count ]; then
echo -e "\n===================="
  echo -e "${GREEN} All tests passed!${RESET}"
else
  echo -e "\n================================================="
  echo -e "${RED} Some tests failed. See '$LOG_FILE' for details.${RESET}"
fi
echo -e "===================="
if [ $total_count -eq 0 ]; then
  success_rate=0
else
  success_rate=$((success_count * 100 / total_count))
fi
echo " ${success_count}/${total_count} (${success_rate}% success)"
echo -e "\n"
