#!/bin/bash
# TODO:
# This script is working but needs to be imporved a little bit with those things:
# - add a command to put dummy data into the database+
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
# 	
# e.g.:	./deploy.sh -e ./path/to/.env
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
ALLOWED_COMMANDS=("help" "stop" "build" "start" "clean" "fclean" "reset" "re")
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
#
# CONTAINER:
ALLOWED_CONTAINERS=("fe" "be" "db" "pa")
#   The container is the service that should be affected by the command.
#   If no container is specified ALL containers will be affected.
#   The allowed containers are:
#
#	| Container  | Service  | Volumes   | Description                                  |
#	|------------|----------|-----------|----------------------------------------------|
#	| `fe`       | frontend |           | The frontend service (nginx, html, css, Js)  |
#	| `be`       | backend  |           | The backend service (django)                 |
#	| `db`       | database | db-volume | The database service (postgres)              |
#	| `pa`       | pgadmin  | pa-volume | The pgadmin service (pgadmin)                |
#
# DOCKER VOLUMES
#   The Script also creates the docker volumes!
#	To work on linux and mac the path to the volumes is different and is set by
#   the function: "check_os" will set the var below:
OS_HOME_PATH=""
#   The volume folders will be created in a folder located at home called:
VOLUME_FOLDER_NAME="barely-some-data"
DB_VOLUME_NAME=db-volume
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
#
# MORE INFO AT:
# https://github.com/rajh-phuyal/42Transcendence/wiki/
# ------------------------------------------------------------------------------
# UPDATE THE VARIABLE BELOW TO CHANGE THE HELP MESSAGE LENGTH OF ./deploy.sh help
HELP_ENDS_AT_LINE=105
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
	    printf "\r\u2705 "
	    echo -e "$message $GR \"$success_message\" $NC"
	else
	    printf "\r\u274C "
	    echo -e "$message $RD \"$failure_message\" $NC"
	    if [ "$fail_continue" == "false" ]; then
	        exit 1  # Exit the script with a failure
	    fi
	fi
	return $exit_code
}

# see comment block above
perform_task_with_spinner() {

	local message="$1..."
    local task="$2"
	# Since the feature sucess msg was added later the following logic happens:
	# If 5 args we have the new sucess msg feature
	# If only 4 args we set it to ""
	if [ "$#" -eq 4 ]; then
	    local success_message=""
	    local failure_message="$3"
	    local fail_continue="${4:-false}"
	elif [ "$#" -eq 5 ]; then
	    local success_message="$3"
		echo "sucess msg: $success_message"
	    local failure_message="$4"
	    local fail_continue="${5:-false}"
	else
	    echo "Error: This function requires 4-5 arguments! Delivered:"
	    echo -e "msg\t\t:$1"
	    echo -e "task\t\t:$2"
	    echo -e "success msg\t:$3"
	    echo -e "fail msg\t:$4"
	    echo -e "fail continue\t:$5"
	    return 1
	fi

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
	for arg in "$@"
	do
		if [ "$arg" == "-e" ]; then
			NEW_ENV_PATH=$MSG_MISSING_PATH	# So the call ./deploy.sh start -e will fail (the path is missing)
			ENV_FLAG_FOUND=true
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
	# 	Containers can't be specified for the commands fclean, re and help
	if [[ "$COMMAND" == "fclean" || "$COMMAND" == "re" || "$COMMAND" == "help" ]] && [[ "$CONTAINERS" != "" ]]; then
		echo -e $OR "Containers can't be specified for the commands fclean, re and help" $NC
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
	echo -e "NEW_ENV_PATH:\t$NEW_ENV_PATH"
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
	elif [[ "$OSTYPE" == "linux"* ]]; then
	    # Any Linux distribution
	    OS_HOME_PATH="$HOME/"
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
		"Flag -e not provided" \
		true; then

		perform_task_with_spinner \
			"Updating environment path to: $NEW_ENV_PATH" \
			'echo "$NEW_ENV_PATH" > "$ENV_PATH_FILE"' \
			"Could not update the environment path." \
			false
		
        # Unset the NEW_ENV_PATH variable
        NEW_ENV_PATH=""
    fi

	# Step 2: Check if a stored path is there and valid
    if perform_task_with_spinner \
		"Searching for storred .env path" \
		'[ -r "$ENV_PATH_FILE" ]' \
		"No environment file path is set. Please provide the path using the -e option." \
		false; then
        
		STORED_ENV_PATH=$(cat "$ENV_PATH_FILE")
		if perform_task_with_spinner \
			"Checking if path ($STORED_ENV_PATH) is valid" \
			'[ -f "$STORED_ENV_PATH" ]' \
			"Stored environment file path is invalid or does not exist: ($STORED_ENV_PATH); update the path using the -e option." \
			false; then

			perform_task_with_spinner \
				"Sourcing env vars from ($STORED_ENV_PATH)" \
				'source "$STORED_ENV_PATH"' \
				"" \
				false
		fi  
	fi
	
    # Step 3: Make a sample test to see if the .env file is loaded
	perform_task_with_spinner \
		"Sample test with <DB_NAME> " \
		'[ ! -z "${DB_NAME:-}" ]' \
		"Sample test with <DB_NAME> failed." "The .env file is not loaded correctly." \
		false
	
	print_header "${BL}" "Checking for the .env file link...${GR}DONE${NC}" 
}

# Used to prepare the folders for the docker volumes
check_path_and_permission()
{
	local path=$1

	if ! perform_task_with_spinner \
		"Checking presents of folder: <$path>" \
		'[ -e "$path" ]' \
		"doesn't exist" \
		true; then

		# Create the folder
		perform_task_with_spinner \
			"Creating folder: <$path>" \
			'mkdir -p $path' \
			"couldn't create folder: <$path>!" \
			false
	fi
	
	# [astein]:
	# Since i had a lot of trouble with the permissions i will set them here
	# accoring to this guide:
	# https://medium.com/@nielssj/docker-volumes-and-file-system-permissions-772c1aee23ca
	perform_task_with_spinner \
		"Changing ownership of folder: <$path>" \
		'sudo chown -R ":1024" "$path"' \
		"couldn't change ownership of folder: <$path>!" \
		false
	
	perform_task_with_spinner \
		"Changing permission of folder: <$path>" \
		'sudo chmod -R 775 "$path"' \
		"couldn't change permission of folder: <$path>!" \
		false

	perform_task_with_spinner \
		"Ensure all future content in the folder <$path> will inherit group ownership" \
		'sudo chmod g+s "$path"' \
		'could not run sudo chmod g+s "$path"' \
		false
}

# Function to check if the folders for the volumes are there
check_volume_folders()
{
	print_header "${YL}" "Checking paths for volumes..."
	check_path_and_permission "TODO"
	print_header "${GR}" "Checking paths for volumes...${GR}DONE${NC}"
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
docker_stop() {
	print_header "${BL}" "Stopping containers: $CONTAINERS..."
	docker-compose --env-file "$STORED_ENV_PATH" stop $CONTAINERS
	print_header "${BL}" "Stopping containers: $CONTAINERS...${GR}DONE${NC}"
}

docker_build() {
	print_header "${BL}" "Building containers: $CONTAINERS"
	docker-compose --env-file "$STORED_ENV_PATH" build $CONTAINERS
	print_header "${BL}" "Building containers: $CONTAINERS...${GR}DONE${NC}"
}

docker_start() {
	docker_stop
	docker_build
	print_header "${BL}" "Starting containers: $CONTAINERS"
	docker-compose --env-file "$STORED_ENV_PATH" up -d $CONTAINERS
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
	docker_clean "$ALLOWED_CONTAINERS"

	print_header "${OR}" "Deleting docker network..."
	docker network rm "$DOCKER_NETWORK" || true
	print_header "${OR}" "Deleting docker network...${GR}DONE${NC}"

	print_header "${OR}" "Stopping and deleting all containers, images, volumes, and network..."
	docker-compose --env-file "$STORED_ENV_PATH" down --rmi all --remove-orphans
	print_header "${OR}" "Stopping and deleting all containers, images, volumes, and network...${GR}DONE${NC}"

	print_header "${OR}" "Deleting docker volumes..."
	docker volume rm "$DB_VOLUME_NAME" || true
	print_header "${OR}" "Deleting docker volumes...${GR}DONE${NC}"

	print_header "${OR}" "Deleting folders of docker volumes..."
	sudo rm -rf "$OS_HOME_PATH$V TODO"
	print_header "${OR}" "Deleting folders of docker volumes...${GR}DONE${NC}"

	print_header "${OR}" "Deltete the link to the environment file..."
	rm -f ".transcendence_env_path"
	print_header "${OR}" "Deltete the link to the environment file...${GR}DONE${NC}"

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


################################################################################
#       Main Script
################################################################################

# Welcome Message
echo ""
perform_task_with_spinner \
	"Welcome to Barely Alive" \
	'sleep 1' \
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
		;;
	re)
		check_setup
		docker_re
		;;
	*)
		print_error "Invalid command: >${COMMAND}<, run >./deploy.sh help< to see the available commands."
		;;
esac
