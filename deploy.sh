#!/bin/bash
# TODO:
# This script is working but needs to be imporved a little bit with those things:
# - sort out all the volumes and mounts we use
#
# BARELY ALIVE
# ------------
# This script is used to deploy the application to a target environment.
#
# USAGE:
#	./deploy.sh [FLAGS] [COMMAND] [CONTAINER]
#
# FLAGS:
#	| Flag  | Description                                                                                                            |
#	|-------|------------------------------------------------------------------------------------------------------------------------|
#	| `-e`  | Path to the .env file. If not set the script will look for the file in the current directory.                          |
#	| `-p`  | This will deploy the app for production!
#
# e.g.:	./deploy.sh -e ./path/to/.env
#
# DOCKER COMPOSE FILES:
COMPOSE_FILE="docker-compose.main.yml"
COMPOSE_FILE_PRODUCTION="docker-compose.prod.yml"
# The domain name will be set according to the flag -p
DOMAIN_NAMES=""
DOMAIN_NAMES_LOCAL=localhost,127.0.0.1
DOMAIN_NAMES_PRODUCTION=ahok.cool,217.160.125.56
#
# this will be updated to "-f $COMPOSE_FILE_PRODUCTION" if -p flag is set
SECOND_COMPOSE_FLAG=""
#
#
# PARSING THE ARGUMENTS:
#   This will populate the global variables:
NEW_ENV_PATH=""
COMMAND=""
CONTAINERS=""
#
# The link to the .env file will be stored in the file:
ENV_PATH_FILE=".transcendence_env_path"
#
# COMMANDS:
ALLOWED_COMMANDS=("help" "stop" "build" "start" "clean" "fclean" "reset" "re" "dummy" "test")
# Join the array in a single string for error messages
ALLOWED_COMMANDS_STR=$(IFS=","; echo "${ALLOWED_COMMANDS[*]}")
#
#   If no command is specified the default command is `start`.
#
#	| Command | Description                                                                                                            |
#	|---------|------------------------------------------------------------------------------------------------------------------------|
#	| `help`  | Prints this message                                                                                                    |
#	| `stop`  | Stops the container(s)                                                                                                 |
#	| `build` | Building the container(s)                                                                                              |
#	| `start` | `stop`, `build`, uping container(s)                                                                                    |
#	| `clean` | `stop`, deletes the container(s) and the image(s)                                                                      |
#	| `fclean`| `clean`, removes docker volumes and docker network, deleting the volume folders, deleting the linkt to the `.env` file |
#	| `reset` | `clean` + `start`                                                                                                      |
#	| `re`    | `fclean` + `start`                                                                                                     |
#	|---------|------------------------------------------------------------------------------------------------------------------------|
#	| `dummy` | Puts dummy data into the database                                                                                      |
#	| `test`  | Starts as script to test the backend api                                                                               |
#
# CONTAINER:
ALLOWED_CONTAINERS=("fe" "be" "db" "pa" "mb")
#   The container is the service that should be affected by the command.
#   If no container is specified ALL containers will be affected.
#   The allowed containers are:
#
#	| Container  | Service  | Volumes                    | Description                                  |
#	|------------|----------|----------------------------|----------------------------------------------|
#	| `fe`       | frontend | media-volume fe-volume     | The frontend service (nginx, html, css, Js)  |
#	| `be`       | backend  | media-volume               | The backend service (django)                 |
#	| `db`       | database | db-volume                  | The database service (postgres)              |
#	| `pa`       | pgadmin  | pa-volume                  | The pgadmin service (pgadmin)                |
#	| `mb`       | redis    | -                          | The redis service                            |
#
# DOCKER VOLUMES
#   The Script also creates the docker volumes!
#	To work on linux and mac the path to the volumes is different and is set by
#   the function: "check_os" will set the var below:
OS_HOME_PATH=""
#   The volume folders will be created in a folder located at home called:
VOLUME_FOLDER_NAME="barely-some-data"
DB_VOLUME_NAME=db-volume
PA_VOLUME_NAME=pa-volume
FE_VOLUME_NAME=fe-volume
MEDIA_VOLUME_NAME=media-volume
export DB_VOLUME_NAME PA_VOLUME_NAME FE_VOLUME_NAME MEDIA_VOLUME_NAME
#
# THE SPINNER
# To make thinks pretty we use a spinner to show that the script is working.
# The spinner allows os to nest a task in it and show a message while the task
# is running. The result of the task will be shown after the spinner stops.
# USAGE:
# 	perform_task_with_spinner "Message" "Task" "Success Message" "Failure Message" "Fail Continue"
#		- Message: The message to show while the task is running
#		- Task: The task to perform
#		- Success Message: The message to show if the task succeeds
#		- Failure Message: The message to show if the task fails
#		- Fail Continue: If the task fails, should the script continue or exit
#
#	Example:
#		perform_task_with_spinner "Checking if the file exists" '[ -f "$FILE" ]' "" "File does not exist" false
#
# The functions start_spinner & stop_spinner are helper functions for the
# spinner and should not be called directly!
#
# Here we store the PID of the spinner process in a global variable so that we
# can kill it if the script is stopped:
SPINNER_PID=""
# ------------------------------------------------------------------------------
#
# OTHER VARIABLES:
#This option ensures that if any command in a pipeline fails, the entire pipeline fails. Without this, only the exit status of the last command in the pipeline would be considered.
set -o pipefail
#
# COLORS
RD='\033[0;31m'
YL='\033[0;33m'
OR='\033[38;5;208m'
GR='\033[0;32m'
BL='\033[0;36m'
NC='\033[0m'
# BOLD
BOLD="\033[1m"
#
# MORE INFO AT:
# https://github.com/rajh-phuyal/42Transcendence/wiki/
# ------------------------------------------------------------------------------
# UPDATE THE VARIABLE BELOW TO CHANGE THE HELP MESSAGE LENGTH OF ./deploy.sh help
# to this line number - 2
HELP_ENDS_AT_LINE=127
# ------------------------------------------------------------------------------

################################################################################
# PRINT FUNCTIONS
# ------------------------------------------------------------------------------
# Function to print a important message in color
print_header() {
	printf "$1 >>> %b${NC}\n" "$2"
}

# Function to print error messages in red and exit the script
print_error() {
	print_header "${RD}" "Error: $1"
    exit 1
}

# URL clickable format function
url() {
    local url=$1
    local text=$2
    echo -e "\e]8;;${url}\a${text}\e]8;;\a"
}
# ------------------------------------------------------------------------------
# SPINNER FUNCTIONS
# ------------------------------------------------------------------------------
# see comment block above
start_spinner() {
    local message="$1"
    local spin='-\|/'

    # Start the spinner in the background
    ( while :; do
        for i in $(seq 0 3); do
            printf "\r%s %s" "${spin:$i:1}" "$message"
            sleep 0.1
        done
    done ) &

    # Save the PID of the spinner process
    SPINNER_PID=$!
}

# see comment block above
stop_spinner() {
    local exit_code=$1
    local message="$2"
    local sucess_message="$3"
    local failure_message="$4"
	local fail_continue="${5:-false}"

    # Kill the spinner process
    if [[ -n "$SPINNER_PID" ]]; then
        kill "$SPINNER_PID" 2>/dev/null
        wait "$SPINNER_PID" 2>/dev/null
        SPINNER_PID=""
    fi

    # Move to the beginning of the line and print the final status
	if [ $exit_code -eq 0 ]; then
	    printf "\r✅ "
	    echo -e "$message $GR ${success_message} $NC"
	else
	    printf "\r❌ "
	    echo -e "$message $RD ${failure_message} $NC"
	    if [ "$fail_continue" == "false" ]; then
	        exit 1  # Exit the script with a failure
	    fi
	fi
	return $exit_code
}

# see comment block above
perform_task_with_spinner() {

	if [ "$#" -ne 5 ]; then
		echo "Error: This function requires arguments! Delivered:"
	    echo -e "msg\t\t:$1"
	    echo -e "task\t\t:$2"
	    echo -e "success msg\t:$3"
	    echo -e "fail msg\t:$4"
	    echo -e "fail continue\t:$5"
	    exit 1
	fi
	local message="$1..."
    local task="$2"
	local success_message="${3:-"done"}"
	local failure_message="$4"
	local fail_continue="${5:-false}"

    # Start the spinner
    start_spinner "$message"

    # Perform the task
    eval "$task"
    local exit_code=$?

	# Stop the spinner and print the final status
    stop_spinner "$exit_code" "$message" "$sucess_message" "$failure_message" "$fail_continue"
	return $?
}

# ------------------------------------------------------------------------------
# SETUP FUNCTIONS
# ------------------------------------------------------------------------------
# As a short pre-setup the arguments are processed via parse_args. This function
# is always called by the main script to assign the global variables:
# - NEW_ENV_PATH
# - COMMAND
# - CONTAINERS
# - COMPOSE_FLAG
#
# The main function check_setup is called by the main script to check if the
# environment is set up correctly. It checks:
# 	- if the .env file is linked and loaded
#	- if the folders for the volumes are there and have the right permissions
# Those checks are bundelt into one function so that the main script can call it
# with one command and only if needed. (The cmds help and fclean dont need it)
#
# Besides the function check_setup all other functions are helper functions and
# should not be called directly!
# ------------------------------------------------------------------------------
parse_args()
{
	print_header "${BL}" "Parsing arguments..."
	NEW_ENV_PATH=""
	COMMAND=""
	CONTAINERS=""
	ENV_FLAG_FOUND=false
	MSG_MISSING_PATH="The -e flag is used but the path is missing. Flag will be ignored!"
    # Add the ip of the machine to the allowed hosts
    LOCAL_IP_OF_MACHINE=$(hostname -I | awk '{print $1}')
    echo -e "LOCAL_IP_OF_MACHINE:\t$LOCAL_IP_OF_MACHINE"
    # Default Domain is $DOMAIN_NAMES_LOCAL
    DOMAIN_NAMES=${DOMAIN_NAMES_LOCAL}","${LOCAL_IP_OF_MACHINE}
    export LOCAL_DEPLOY=TRUE
	for arg in "$@"
	do
		if [ "$arg" == "-e" ]; then
			echo "found flag 'e'"
			NEW_ENV_PATH=$MSG_MISSING_PATH	# So the call ./deploy.sh start -e will fail (the path is missing)
			ENV_FLAG_FOUND=true
		elif [ "$arg" == "-p" ]; then
		    print_header "${RD}" " ################################## "${NC}
		    print_header "${RD}" " #        (found flag '-p')       # "${NC}
		    print_header "${RD}" " # !! DEPLOYING FOR PRODUCTION !! # "${NC}
		    print_header "${RD}" " ################################## "${NC}
			SECOND_COMPOSE_FLAG="-f ""$COMPOSE_FILE_PRODUCTION"
            echo -e "DEPLOY FOR PRODUCTION: set SECOND_COMPOSE_FLAG to:$RD$SECOND_COMPOSE_FLAG$NC"
            DOMAIN_NAMES=$DOMAIN_NAMES_PRODUCTION
            echo -e "DEPLOY FOR PRODUCTION: set DOMAIN_NAMES to:$RD$DOMAIN_NAMES$NC"
            export LOCAL_DEPLOY=FALSE
            echo -e "DEPLOY FOR PRODUCTION: set LOCAL_DEPLOY to:$RD$LOCAL_DEPLOY$NC"
		elif [ "$ENV_FLAG_FOUND" == true ]; then
			NEW_ENV_PATH=$arg
			ENV_FLAG_FOUND=false
		elif [ "$COMMAND" == "" ]; then
			COMMAND=$arg
		else
			if [ -z "$CONTAINERS" ]; then
            	CONTAINERS="$arg"
        	else
            	CONTAINERS="$CONTAINERS $arg"
        	fi
		fi
	done

	# 	checking the COMMAND
	COMMAND="${COMMAND:-start}" # If no command is specified the default command is start
	is_cmd_valid=false
    for allowed_cmd in "${ALLOWED_COMMANDS[@]}"; do
        if [[ "$COMMAND" == "$allowed_cmd" ]]; then
            is_cmd_valid=true
			break
        fi
    done
    if [ "$is_cmd_valid" == false ]; then
		print_error "Invalid command: '${COMMAND}' (only '${ALLOWED_COMMANDS_STR}' are allowed!)"
	fi
	echo -e "COMMAND:\t$COMMAND"

	# 	checking the CONTAINERS
	# 	Containers can't be specified for the commands fclean, re, help and dummy
	if [[ "$COMMAND" == "dummy" || "$COMMAND" == "fclean" || "$COMMAND" == "re" || "$COMMAND" == "help" ]] && [[ "$CONTAINERS" != "" ]]; then
		echo -e $OR "Containers can't be specified for the commands fclean, re, help and dummy" $NC
		echo -e $OR "The input '$CONTAINERS' will be ignored" $NC
		CONTAINERS=""
	fi

	if [ -z "$CONTAINERS" ]; then
	    for container in "${ALLOWED_CONTAINERS[@]}"; do
	        CONTAINERS="$CONTAINERS $container"
	    done
	    CONTAINERS="${CONTAINERS# }"  # Trim leading space
	else
	    # Containers can only be those from the $ALLOWED_CONTAINERS list
	    for item in $CONTAINERS; do
	        if ! [[ " ${ALLOWED_CONTAINERS[*]} " =~ " $item " ]]; then
	            print_error "Invalid container: '$item' (only '${ALLOWED_CONTAINERS[*]}' are allowed!)"
	        fi
	    done
	fi

	echo -e "CONTAINERS:\t$CONTAINERS"

	#	checking the ENV_PATH
	if [ "$NEW_ENV_PATH" == "$MSG_MISSING_PATH" ]; then
		echo -e $OR $MSG_MISSING_PATH $NC
		NEW_ENV_PATH=""
	fi
    if [ "$NEW_ENV_PATH" != "" ]; then
        echo -e "NEW_ENV_PATH:\t$NEW_ENV_PATH"
    fi

    # Export the DOMAIN_NAMES
    export DOMAIN_NAMES
    echo -e "DOMAIN_NAMES:\t$DOMAIN_NAMES"
	# Exporting the user and the group so that docker compse can use this
	export UID=$(id -u)
	export GID=$(id -g)
	print_header "${BL}" "Parsing arguments...${GR}DONE${NC}"
}

check_setup() {
	check_os
	check_env_link
	check_volume_folders
}

# To set the volume location we need to differ between linux and mac
check_os()
{
	OS_HOME_PATH=""
	if [[ "$OSTYPE" == "darwin"* ]]; then
	    # macOS
	    OS_HOME_PATH="/Users/$(whoami)/"
		IS_MACOS=true
	elif [[ "$OSTYPE" == "linux"* ]]; then
	    # Any Linux distribution
	    OS_HOME_PATH="$HOME/"
		IS_MACOS=false
	else
		print_error "Unsupported OS: $OSTYPE"
	fi
	perform_task_with_spinner \
		"Setting the home path for this OS" \
		'[ -n "$OS_HOME_PATH" ]' \
		"$OS_HOME_PATH" \
		"Could not figure out home path on this os!" \
		false
}

# Function to check (and update) the link to the .env file which will then be
# sourced and sample tested with $DB_NAME
check_env_link() {
	print_header "${BL}" "Checking for the .env file link..."

	# Step 1: Check if the -e flag is provided
	if perform_task_with_spinner \
		"Checking if the -e flag is provided" \
		'[ -n "$NEW_ENV_PATH" ]' \
		"" \
		"Flag -e not provided" \
		true; then

		perform_task_with_spinner \
			"Updating environment path to: $NEW_ENV_PATH" \
			'echo "$NEW_ENV_PATH" > "$ENV_PATH_FILE"' \
			"" \
			"Could not update the environment path." \
			false

        # Unset the NEW_ENV_PATH variable
        NEW_ENV_PATH=""
    fi

	# Step 2: Check if a stored path is there and valid
    if perform_task_with_spinner \
		"Searching for storred .env path" \
		'[ -r "$ENV_PATH_FILE" ]' \
		"" \
		"No environment file path is set. Please provide the path using the -e option." \
		false; then

		STORED_ENV_PATH=$(cat "$ENV_PATH_FILE")
		if perform_task_with_spinner \
			"Checking if path ($STORED_ENV_PATH) is valid" \
			'[ -f "$STORED_ENV_PATH" ]' \
			"" \
			"Stored environment file path is invalid or does not exist: ($STORED_ENV_PATH); update the path using the -e option." \
			false; then

			perform_task_with_spinner \
				"Sourcing env vars from ($STORED_ENV_PATH)" \
				'source "$STORED_ENV_PATH"' \
				"" \
				"" \
				false
		fi
	fi

    # Step 3: Make a sample test to see if the .env file is loaded
	perform_task_with_spinner \
		"Sample test with <DB_NAME> " \
		'[ ! -z "${DB_NAME:-}" ]' \
		"$DB_NAME" \
		"Sample test with <DB_NAME> failed. The .env file is not loaded correctly." \
		false

	# Step 4: Export the VOLUME_ROOT_PATH
    perform_task_with_spinner \
        "Exporting the VOLUME_ROOT_PATH: "$OS_HOME_PATH$VOLUME_FOLDER_NAME/"" \
        'export VOLUME_ROOT_PATH="$OS_HOME_PATH$VOLUME_FOLDER_NAME/"' \
        "done" \
        "failed to export VOLUME_ROOT_PATH" \
        false

	#if perform_task_with_spinner \
	#	"Checking if env VOLUME_ROOT_PATH already exists" \
	#	"grep -q '^VOLUME_ROOT_PATH=' '$STORED_ENV_PATH'" \
	#	"" \
	#	"" \
	#	true; then
	#		perform_task_with_spinner \
	#			"Updating var VOLUME_ROOT_PATH in env file" \
	#			"sed -i.bak 's|^VOLUME_ROOT_PATH=.*|VOLUME_ROOT_PATH=\"$OS_HOME_PATH$VOLUME_FOLDER_NAME/\"|g' '$STORED_ENV_PATH' && rm -f '$STORED_ENV_PATH.bak'" \
	#			"VOLUME_ROOT_PATH=\"$OS_HOME_PATH$VOLUME_FOLDER_NAME/\"" \
	#			"failed to update var VOLUME_ROOT_PATH in env file" \
	#			false
	#	else
	#		perform_task_with_spinner \
	#		"Adding var VOLUME_ROOT_PATH to env file" \
	#		"echo 'VOLUME_ROOT_PATH=\"$OS_HOME_PATH$VOLUME_FOLDER_NAME/\"' >> '$STORED_ENV_PATH'" \
	#		"VOLUME_ROOT_PATH=\"$OS_HOME_PATH$VOLUME_FOLDER_NAME/\"" \
	#		"failed to add var VOLUME_ROOT_PATH to env file" \
	#		false
	#fi

	# Step 5: Source again
	perform_task_with_spinner \
		"Sourcing updated env vars from ($STORED_ENV_PATH)" \
		"source $STORED_ENV_PATH" \
		"" \
		"couldn't source env file!" \
		false

    # Step 5: Make a sample test to see if the .env file is loaded
	perform_task_with_spinner \
		"Sample test with <VOLUME_ROOT_PATH> " \
		'[ ! -z "${VOLUME_ROOT_PATH:-}" ]' \
		"$VOLUME_ROOT_PATH" \
		"Sample test with <VOLUME_ROOT_PATH> failed. The .env file is not loaded correctly." \
		false
	print_header "${BL}" "Checking for the .env file link...${GR}DONE${NC}"
}

# Used to prepare the folders for the docker volumes
check_path_and_permission()
{
	local path=$1
	path_formated=$(url "file://$path" "$path")

	if ! perform_task_with_spinner \
		"Checking presents of folder: $path_formated ..." \
		'[ -e "$path" ]' \
		"is there" \
		"doesn't exist" \
		true; then

		# Create the folder
		perform_task_with_spinner \
			" ...creating the folder" \
			'mkdir -p $path' \
			"created" \
			"couldn't create folder: $path_formated!" \
			false
	fi
}

# Function to check if the folders for the volumes are there
check_volume_folders()
{
	print_header "${YL}" "Checking paths for volumes..."
	check_path_and_permission "$OS_HOME_PATH$VOLUME_FOLDER_NAME/$DB_VOLUME_NAME/"
	check_path_and_permission "$OS_HOME_PATH$VOLUME_FOLDER_NAME/$PA_VOLUME_NAME/"
    check_path_and_permission "$OS_HOME_PATH$VOLUME_FOLDER_NAME/$FE_VOLUME_NAME/"
	check_path_and_permission "$OS_HOME_PATH$VOLUME_FOLDER_NAME/$MEDIA_VOLUME_NAME/"
	print_header "${GR}" "Checking paths for volumes...${GR}DONE${NC}"
}

print_server_urls()
{
    IFS=','
    for DOMAIN in $DOMAIN_NAMES_LOCAL; do
        echo -e "${GR}" "\tWebsite reachable at: ${BL}$(url "https://$DOMAIN" "$DOMAIN")${NC}"
    done
}

# ------------------------------------------------------------------------------
# DOCKER BASIC FUNCTIONS
#	stop [contaier]			| Stops the container(s)
#	build [contaier]		| Building the container(s)
#	start [contaier]		| down build up [THIS IS THE DEFAULT TARGET]
#	clean [contaier]		| down + Deletes the container(s) and the image(s)
#	fclean 					| Deletes the container(s) + Volumes + Network
#	reset [container]		| clean + start
#	re 						| fclean + start
# ------------------------------------------------------------------------------
# 	insert_dummy_data		| Puts dummy data into the database
# ------------------------------------------------------------------------------
docker_stop() {
	print_header "${BL}" "Stopping containers: $CONTAINERS..."
	docker compose -f="$COMPOSE_FILE" $SECOND_COMPOSE_FLAG --env-file="$STORED_ENV_PATH" stop $CONTAINERS
	print_header "${BL}" "Stopping containers: $CONTAINERS...${GR}DONE${NC}"
}

docker_build() {
	print_header "${BL}" "Building containers: $CONTAINERS"
	docker compose -f="$COMPOSE_FILE" $SECOND_COMPOSE_FLAG --env-file="$STORED_ENV_PATH" build $CONTAINERS
	print_header "${BL}" "Building containers: $CONTAINERS...${GR}DONE${NC}"
}

docker_start() {
	docker_stop
	docker_build
	print_header "${BL}" "Starting containers: $CONTAINERS"
	docker compose -f="$COMPOSE_FILE" $SECOND_COMPOSE_FLAG --env-file="$STORED_ENV_PATH" up -d $CONTAINERS
	print_header "${BL}" "Starting containers: $CONTAINERS...${GR}DONE${NC}"
}

docker_clean() {
	docker_stop
	print_header "${OR}" "Deleting containers..."
	docker container rm $CONTAINERS || true
	print_header "${OR}" "Deleting containers...${GR}DONE${NC}"
	print_header "${OR}" "Deleting images..."
	docker image rm $CONTAINERS || true
	print_header "${OR}" "Deleting images...${GR}DONE${NC}"
}

docker_fclean() {
	# Prompt user for confirmation
	print_header "${RD}" "ARE YOU SURE YOU WANT TO DELETE ALL CONTAINERS, IMAGES, VOLUMES, AND THE DOCKER NETWORK (y/n): "
	read -p "choose: " confirm
	if [[ "$confirm" != "y" ]]; then
		print_header "${RD}" "Operation cancelled."
		exit 1
	fi
	print_header "${OR}" "Stopping and deleting all containers, images, volumes, and network..."
	docker_clean "$ALLOWED_CONTAINERS"

	print_header "${OR}" "Deleting docker network..."
	docker network rm "$DOCKER_NETWORK" || true
	print_header "${OR}" "Deleting docker network...${GR}DONE${NC}"

	docker compose -f="$COMPOSE_FILE" $SECOND_COMPOSE_FLAG --env-file="$STORED_ENV_PATH" down --rmi all --remove-orphans

	print_header "${OR}" "Stopping and deleting all containers, images, volumes, and network...${GR}DONE${NC}"

	print_header "${OR}" "Deleting docker volumes..."
	docker volume rm "$DB_VOLUME_NAME" || true
	docker volume rm "$PA_VOLUME_NAME" || true
	docker volume rm "$FE_VOLUME_NAME" || true
	docker volume rm "$MEDIA_VOLUME_NAME" || true
	print_header "${OR}" "Deleting docker volumes...${GR}DONE${NC}"

	print_header "${OR}" "Deleting folder of docker volumes...($OS_HOME_PATH$VOLUME_FOLDER_NAME/)"
	rm -rf "$OS_HOME_PATH$VOLUME_FOLDER_NAME/"
	print_header "${OR}" "Deleting folder of docker volumes...${GR}DONE${NC}"

	print_header "${OR}" "Delete the link to the environment file..."
	rm -f ".transcendence_env_path"
	print_header "${OR}" "Delete the link to the environment file...${GR}DONE${NC}"

	print_header "${RD}" "Do u additionaly do a full clean aka 'docker system prune -a --volumes -f' (y/n): "
	read -p "choose: " confirm
	if [[ "$confirm" == "y" ]]; then
		print_header "${OR}" "Performing a full system prune to remove all remaining images, containers, volumes, and networks..."
		docker system prune -a --volumes -f
		print_header "${OR}" "Performing a full system prune to remove all remaining images, containers, volumes, and networks...${GR}DONE${NC}"
	else
		print_header "${RD}" "Operation cancelled."
	fi

	# print_success "All containers, images, volumes, and network have been deleted."
	print_header "${RD}" "All containers, images, volumes, and network have been deleted successfully."
}

docker_reset() {
	docker_clean
	docker_start
}

docker_re() {
	#Save the old env path since fclean will delete it
	ENV_BUFFER=$(cat "$ENV_PATH_FILE")

	# Do the fclean
	docker_fclean

	# Restore the old env path
	parse_args "-e" "$ENV_BUFFER"
	ENV_BUFFER=""

	# Check the setup to make sure the .env file is loaded and the volumes are there
	check_setup

	#Start the containers
	docker_start
}

check_healthy() {
    if [[ " ${ALLOWED_CONTAINERS[*]} " =~ " $1 " ]]; then
        for index in {1..15}; do
            if perform_task_with_spinner \
                "Checking if the container $1 is healthy (try:${index}/15)" \
                "[ $(docker inspect --format='{{.State.Health.Status}}' $1 2>/dev/null) = "healthy" ]" \
                "$1 container is up and healthy" \
                "$1 container isn't running (or unhealthy)!" \
                true; then
                return 0 # Success
            fi
            sleep 1
        done
        return 1
    else
        print_error "Invalid container: '$1' (only '${ALLOWED_CONTAINERS[*]}' are allowed!)"
        return 1
    fi
}

insert_dummy_data() {
    if ! check_healthy "db"; then
        print_header "${RD}" "The database is not running (or unhealthy)!\nRun './deploy.sh start db' first!"
        exit 1
    fi

	print_header "${RD}" "ARE YOU SURE YOU WANT TO DELETE ALL THE DATA FROM THE DATABASE AND INSERT DUMMY DATA INSTEAD (y/n): "
	read -p "choose: " confirm
	if [[ "$confirm" != "y" ]]; then
		print_header "${RD}" "Operation cancelled."
		exit 1
	fi

	print_header "${OR}" "Inserting dummy data into the database..."
	docker exec -it db  bash /tools/create_dummy.sh
	print_header "${OR}" "Inserting dummy data into the database...${GR}DONE${NC}"
}

run_test() {
    services=("db" "be" "fe")
    for service in "${services[@]}"; do
        if ! check_healthy "$service"; then
            print_header "${RD}" "The $service is not running (or unhealthy)!\nRun './deploy.sh start $service' first!"
            exit 1
        fi
    done

    print_header "${BL}" "Starting the tester...${NC}"
    bash "$(dirname "$(realpath "$0")")/Tester/tester.sh"
}

################################################################################
#       Main Script
################################################################################

# Welcome Message
echo ""
perform_task_with_spinner \
	"Welcome to Barely Alive" \
	'sleep 0.1' \
	"Let's go" \
	"Failed to print welcome message." \
	false

# Assign the global variables from the arguments
parse_args "$@"

# Execute the command
case "$COMMAND" in
	help)
		cat ./deploy.sh | head -n ${HELP_ENDS_AT_LINE}
		;;
	start)
		check_setup
		docker_start
        print_server_urls
		;;
	stop)
		check_setup
		docker_stop
		;;
	clean)
		check_setup
		docker_clean
		;;
	fclean)
		check_setup
		docker_fclean
		;;
	build)
		check_setup
		docker_build
		;;
	reset)
		check_setup
		docker_reset
        print_server_urls
		;;
	re)
		check_setup
		docker_re
        print_server_urls
		;;
	dummy)
		insert_dummy_data
		;;
    test)
        run_test
        ;;
	*)
		print_error "Invalid command: >${COMMAND}<, run >./deploy.sh help< to see the available commands."
		;;
esac

print_header "${BL}" "DONE - Barely Alive"
