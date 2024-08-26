#!/bin/bash
# TODO:
# This script is working but needs to be imporved a little bit with those things:
# - Check if the folders for the volumes are there so dont print the messages
# - Therfore maybe put them in a function
# - add a command to put dummy data into the database+
# - sort out all the volumes and mounts we use
# - include healthcheck for the containers proabably in the doocker-compose file

# BARELY ALIVE
# ------------
# This script is used to deploy the application to a target environment.
# It handels all the different docker containers and u always can specify
# the action for a specific container. Those are:
#
#	CODE	SERVICE		CONTAINER NAME	VOLUMES
#	------|-----------|----------------|-------------
#	fe		frontend	fr
#	be		backend		be
#	db		database	db				db_volume
#	pa		pgadmin 	pa				pa_volume
#
# COMMANDS:
# (If no container is specified ALL containers will be affected)
#	| Option  | Description                                                                                                            |
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
# ENVIROMENT VARIABLES
# The used env file will be stored in the file
ENV_PATH_FILE=".transcendence_env_path"
#
# if its not set u need to run with the flag:
#	./deploy.sh -e <pathToEnvFile>
#
# MORE INFO AT:
# https://github.com/rajh-phuyal/42Transcendence/wiki/
# ------------------------------------------------------------------------------
# UPDATE THE VARIABLE BELOW TO CHANGE THE HELP MESSAGE LENGTH OF ./deploy.sh help
HELP_ENDS_AT_LINE=45

# Script should stop if something goes wrong:
set -e 				#This option causes the script to exit immediately if any command exits with a non-zero status (i.e., an error). This is useful because it prevents the script from continuing in an unpredictable state after a failure.
set -o pipefail		#This option ensures that if any command in a pipeline fails, the entire pipeline fails. Without this, only the exit status of the last command in the pipeline would be considered.

# VARIABLES
# ------------------------------------------------------------------------------
# COLORS
RD='\033[0;31m'
YL='\033[0;33m'
OR='\033[38;5;208m'
GR='\033[0;32m'
NC='\033[0m'

FE_CONTAINER_NAME="fe"
BE_CONTAINER_NAME="be"
DB_CONTAINER_NAME="db"
PA_CONTAINER_NAME="pa"
ALL_SERVICES="${FE_CONTAINER_NAME} ${BE_CONTAINER_NAME} ${DB_CONTAINER_NAME} ${PA_CONTAINER_NAME}"

# Docker Volumes
VOLUME_ROOT_PATH="$HOME/barely-some-data/"
DB_VOLUME_NAME=db-volume
PA_VOLUME_NAME=pa-volume

DB_VOLUME_PATH="${VOLUME_ROOT_PATH}${DB_VOLUME_NAME}"
PA_VOLUME_PATH="${VOLUME_ROOT_PATH}${PA_VOLUME_NAME}"

# Global variable to hold remaining arguments
# Used by check_env_link
REMAINING_ARGS=()

# FUNCTIONS
# ------------------------------------------------------------------------------ 
# Function to print a important message in color
print_header() {
    printf "$1 >>> %s${NC}\n" "$2"
}

# Function to print error messages in red
print_error() {
    echo -e "\u274C "  # Red cross emoji
	echo $1
}

print_success() {
	echo -en "\u2705 "  # Green checkmark emoji
	echo $1
}

print_fail() {
	print_header "${RD}" "Failed: $1"
}

# Function to check if an .env file is linked
check_env_link() {
	# Initialize an empty array to hold the remaining arguments
    local args=("$@")

	# Step 1: Check if the -e flag is provided
    if [ "${args[0]:-}" == "-e" ] && [ -n "${args[1]:-}" ]; then
        # Save environment path
        echo "${args[1]}" > "$ENV_PATH_FILE"
        print_success "Environment path updated to: ${args[1]}"
        
        # Remove the first two arguments (-e and the path)
        args=("${args[@]:2}")
    fi

	# Step 2: Check if a stored path is there and valid
    if [ ! -f "$ENV_PATH_FILE" ]; then
        print_fail "No environment file path is set. Please provide the path using the -e option."
        return 1
    else
        STORED_ENV_PATH=$(cat "$ENV_PATH_FILE")
        if [ ! -f "$STORED_ENV_PATH" ]; then
            print_fail "Stored environment file path is invalid or does not exist: $STORED_ENV_PATH"
            return 1
        fi
        # Load the .env file into this script
        source "$STORED_ENV_PATH"
        print_success "Environment file loaded from: $STORED_ENV_PATH"
    fi

    # Step 3: Make a sample test to see if the .env file is loaded
    if [ -z "${DB_NAME:-}" ]; then
		print_fail "Sample test with DB_NAME"
        print_error "The .env file is not loaded correctly. Sample test with DB_NAME failed."
	else
		print_success "Sample test with DB_NAME"
    fi

    # Assign remaining arguments to the global variable
    REMAINING_ARGS=("${args[@]}")
}

# DOCKER BASIC FUNCTIONS
#	start [contaier]		| down build up [THIS IS THE DEFAULT TARGET]
#	stop [contaier]			| Stops the container(s)
#	clean [contaier]		| down + Deletes the container(s) and the image(s)
#	fclean 					| Deletes the container(s) + Volumes + Network
#	build [contaier]		| Building the container(s)
#	reset [container]		| clean + start
#	re 						| fclean + start

docker_stop() {
	print_header "${YL}" "Stopping containers: $1"
	docker-compose --env-file "$STORED_ENV_PATH" stop $1
}

docker_build() {
	print_header "${GR}" "Building containers: $1"
	docker-compose --env-file "$STORED_ENV_PATH" build $1
}

docker_start() {
	docker_stop "$1"
	docker_build "$1"
	print_header "${GR}" "Starting containers: $1"
	docker-compose --env-file "$STORED_ENV_PATH" up -d $CONTAINER
}

docker_clean() {
	docker_stop "$1"
	print_header "${OR}" "Deleting containers..."
	docker container rm $1 || true
	print_header "${OR}" "Deleting images..."
	docker image rm $1 || true
}

docker_fclean() {    
	# Prompt user for confirmation
	print_header "${RD}" "ARE YOU SURE YOU WANT TO DELETE ALL CONTAINERS, IMAGES, VOLUMES, AND THE DOCKER NETWORK (y/n): "
    read -p "choose: " confirm
    if [[ "$confirm" != "y" ]]; then
        print_header "${RD}" "Operation cancelled."
        return 1
    fi
	print_header "${RD}" "Force cleaning containers and volumes..."
	docker_clean "$ALL_SERVICES"
	print_header "${OR}" "Deleting docker network..."
	docker network rm "$DOCKER_NETWORK" || true
	print_header "${OR}" "Deleting docker volumes..."
	docker volume rm "$DB_VOLUME_NAME" || true
	docker-compose --env-file "$STORED_ENV_PATH" down -v --rmi all --remove-orphans
	print_header "${OR}" "Deleting folders of docker volumes..."
	sudo rm -rf ${VOLUME_ROOT_PATH}
	print_header "${OR}" "Deltete the link to the environment file..."
	rm -f ".transcendence_env_path"
	print_success "All containers, images, volumes, and network have been deleted."
}

docker_reset() {
	docker_clean "$1"
	docker_start "$1"
}

# TODO: Doesnt work since the .env file will be deleted during fclean...
# TODO: Also the volumes wont be created again atm...
# TODO: Work around is to call fclean then -e and then start
docker_re() {
	docker_fclean "$ALL_SERVICES"
	docker_start "$ALL_SERVICES"
}


################################################################################
#       Main Script
################################################################################

# CHECK FOR ENV FILE and process arguments
check_env_link "$@"

# UPDATE ARGUMENTS: Use the global REMAINING_ARGS variable
# Set positional parameters for further use
set -- "${REMAINING_ARGS[@]}"

# CHECK IF FOLDERS ARE THERE AND FILES AND OTHER STUFF HERE
# create folders for volumes if they don't exist yet:
print_header ${GR} "Creating folder for volumes at: $DB_VOLUME_PATH"
mkdir -p ${DB_VOLUME_PATH}
#print_header ${OR} "Changing ownership of volume folder at: $DB_VOLUME_PATH"
## TODO
## THIS SHOULD NOT BE DONE IF FOLDER EXISTS
#chown -R "$USER:$USER" "${DB_VOLUME_PATH}"

print_header ${GR} "Creating folders for volumes at: $PA_VOLUME_PATH"
mkdir -p ${PA_VOLUME_PATH}
#print_header ${OR} "Changing ownership of volume folder at: $PA_VOLUME_PATH"
#chown -R "$USER:$USER" "${PA_VOLUME_PATH}"

# Main logic for Docker commands
COMMAND="${1:-start}"  				# Default to 'start' if no command is provided
CONTAINER="${2:-$ALL_SERVICES}"	# Optional container name

case "$COMMAND" in
	help)
        cat ./deploy.sh | head -n ${HELP_ENDS_AT_LINE}
        ;;
    start)
        docker_start "$CONTAINER"
        ;;
    stop)
        docker_stop "$CONTAINER"
        ;;
    clean)
		docker_clean "$CONTAINER"
        ;;
    fclean)
		docker_fclean
        ;;
    build)
        docker_build "$CONTAINER"
        ;;
	reset)
		docker_reset "$CONTAINER"
        ;;
    re)
		docker_re
        ;;
    *)
		print_error "Invalid command: >$COMMAND<, run >./deploy.sh help< to see the available commands."
        ;;
esac
