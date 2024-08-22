#!/bin/bash

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
#	start [contaier]		| down build up [THIS IS THE DEFAULT TARGET]
#	stop [contaier]			| Stops the container(s)
#	clean [contaier]		| down + Deletes the container(s) and the image(s)
#	fclean [contaier]		| Deletes the container(s) + Volumes + Network
#	build [contaier]		| Building the container(s)
#	re [container]			| fclean + start
#
# ENVIROMENT VARIABLES
# The used env file will be stored in the file
ENV_PATH_FILE=".transcendence_env_path"
#
# if its not set u need to run with the flag:
#	./deploy.sh -e <pathToEnvFile>
#
HELP_ENDS_AT_LINE=30

# Script should stop if something goes wrong:
set -euo pipefail


# VARIABLES
# ------------------------------------------------------------------------------
# COLORS
RD='\033[0;31m'
YL='\033[0;33m'
OR='\033[38;5;208m'
GR='\033[0;32m'
NC='\033[0m'

FRONTEND_CONTAINER_NAME="fe"
BACKEND_CONTAINER_NAME="be"
DATABASE_CONTAINER_NAME="db"
PGADMIN_CONTAINER_NAME="pa"
ALL_SERVICES="${FRONTEND_CONTAINER_NAME} ${BACKEND_CONTAINER_NAME} ${DATABASE_CONTAINER_NAME} ${PGADMIN_CONTAINER_NAME}"
DATABASE_VOLUME_NAME=db-volume

# FUNCTIONS
# ------------------------------------------------------------------------------ 
# Function to print a important message in color
print_header() {
    printf "$1 >>> %s${NC}\n" "$2"
}

# Function to print error messages in red
print_error() {
    print_header "${RD}" "Error: $1"
    exit 1
}

# Function to save the environment path
save_env_path() {
    echo "$1" > "$ENV_PATH_FILE"
	STORED_ENV_PATH=$(cat "$ENV_PATH_FILE")
}

# Function to check if the stored path is valid
validate_stored_path() {
    if [ ! -f "$1" ]; then
        print_error "Stored environment file path is invalid or does not exist: $1"
    fi
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
	docker volume rm "$DATABASE_VOLUME_NAME" || true
	docker-compose --env-file "$STORED_ENV_PATH" down -v --rmi all --remove-orphans
}

docker_reset() {
	docker_clean "$1"
	docker_start "$1"
}

docker_re() {
	docker_fclean "$ALL_SERVICES"
	docker_start "$ALL_SERVICES"
}


################################################################################
#       Main Script
################################################################################

# CHECK FOR ENV FILE
# ------------------------------------------------------------------------------ 
# Check if the -e flag is provided to set a new environment path
if [ "${1:-}" == "-e" ] && [ -n "${2:-}" ]; then
    save_env_path "$2"
    print_header "${GR}" "Environment path saved: $2"
elif [ -f "$ENV_PATH_FILE" ]; then
    STORED_ENV_PATH=$(cat "$ENV_PATH_FILE")
    validate_stored_path "$STORED_ENV_PATH"
    echo "Using stored environment file: $STORED_ENV_PATH"
else
    print_error "No environment file path is set. Please provide the path using the -e option."
fi
print_header ${GR} "Using environment file: $STORED_ENV_PATH"

# Load the .env file into this script (and update some variable):
source "$STORED_ENV_PATH"

# TODO
# CHECK IF FOLDERS ARE THERE AND FILES AND OTHER STUFF HERE

# Main logic for Docker commands
COMMAND="${1:-start}"  				# Default to 'start' if no command is provided
CONTAINER="${2:-$ALL_SERVICES}"	# Optional container name

case "$COMMAND" in
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
        print_error "Invalid command: $COMMAND. Valid commands are start, stop, clean, fclean, build, re."
        ;;
esac







# To print the top of this file
# cat ./deploy.sh | head -n ${HELP_ENDS_AT_LINE}



