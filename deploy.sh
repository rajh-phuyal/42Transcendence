#!/bin/bash

# This script is used to deploy the application to a target environment.

set -euo pipefail
RD='\033[0;31m'
YL='\033[0;33m'
GR='\033[0;32m'
NC='\033[0m'

TARGET_LIST=("database" "backend" "frontend")

DATABASE_CONTAINER_NAME="transcendence-postgres"
BACKEND_CONTAINER_NAME="transcendence-django"
FRONTEND_CONTAINER_NAME="transcendence-nginx"

DOCKER_NETWORK=transcendence-network

LOG_FOLDER="Logs"
LOG_FILE="$LOG_FOLDER/deploy.log"

USAGE=$YL"Usage: ./deploy.sh [OPTIONS]
Options:
    -h |  Display this message
    -t |  Service to be installed. (default: all || ${TARGET_LIST[*]})
    -c |  Relative path to the .env file"$NC

#######################################
#	   Utility functions
#######################################

function echo_log { 
  echo -e "$(date +%Y%m%d.%H%M%S): ${@:-NO_MESSAGE_SUPPLIED} ${NC}" 2>&1 | tee -a $LOG_FILE
}

function echo_log_exit {
  echo_log "${RD}ERROR - ${@:-NO_MESSAGE_SUPPLIED}" 
  echo -e $USAGE
  exit 1
}

function exec_log {
  PARAMS="$@"
  echo -e "$(date +%Y%m%d.%H%M%S): ${GR} $PARAMS" ${NC} 2>&1 | tee -a $LOG_FILE
  eval $PARAMS 2>&1 | tee -a $LOG_FILE
}

function check_cli_args {

    echo_log "Checking CLI arguments: $@"
    TARGET_ENV=()
    CONFIG_FILE=""
    
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            -t)
                if [[ "$#" -gt 1 && "$2" != -* ]]; then
                    IFS=',' read -ra TARGET_VALUES <<< "$2"
                    for val in "${TARGET_VALUES[@]}"; do
                        TARGET_ENV+=("$val")
                    done
                    shift 2
                else
                    echo_log_exit "-t option requires a non-empty argument."
                fi
                ;;
            -c)
                if [[ "$#" -gt 1 && "$2" != -* ]]; then
                    CONFIG_FILE="$2"
                    shift 2
                else
                    echo_log_exit "-c option requires a non-empty argument."
                fi
                ;;
            -h)
                echo -e "$USAGE"
                exit 0
                ;;
            *)
				echo_log_exit "Unknown option: $1"
                ;;
        esac
    done

    if [ -z "$CONFIG_FILE" ]; then
		echo_log_exit "ENV must be specified."
    fi

    if [ ${#TARGET_ENV[@]} -eq 0 ]; then
        TARGET_ENV=("${TARGET_LIST[@]}")
    fi

	# Remove duplicates
	TARGET_ENV=($(echo "${TARGET_ENV[@]}" | tr ' ' '\n' | awk '!seen[$0]++'))
}

function  create_folder_if_not_exists() {
    local folder_path="$1"
    if [ ! -d "$folder_path" ]; then
        echo_log "Folder does not exist. Creating \"$folder_path\""
        mkdir -p "$folder_path"
	else
		echo_log "Log folder found: \"$folder_path\""
    fi
}

function load_env_file {
	local env_file="$1"
	if [ -f "$env_file" ]; then
		echo_log "Loading environment variables from \"$env_file\""
		source "$env_file"
	else
		echo_log_exit "Environment file \"$env_file\" does not exist."
	fi
	echo_log "Environment variables loaded."
}

function build_docker_image {
  local NAME=${1}
  local TAG=${1}
  local DOCKERFILE=${2}
  local CONTEXT=${3}
  echo_log "Building Docker image: $NAME"
  exec_log docker build -f $DOCKERFILE -t $NAME $CONTEXT
}

function is_docker_container_running {
  echo -e $"Checking if container is running: $1"
  local NAME=${1}
  if [ "$(docker ps -qa -f name=^$NAME$)" ]; then # Check if container exists
	echo_log "Found container: $NAME"
	if [ "$(docker ps -q -f name=^$NAME$)" ]; then # Check if container is running
		return 0
	fi
  fi
  return 1
}

function stop_and_rm_docker_container {
  # $1 Docker container name
  local NAME=${1}
  if [ "$(docker ps -qa -f name=^$NAME$)" ]; then # Check if container exists
	echo_log "Found container: $NAME"
    if [ "$(docker ps -q -f name=^$NAME$)" ]; then # Check if container is running
        echo_log "Stopping running container:  $NAME"
        exec_log docker stop $NAME;
		exec_log docker rm $NAME;
    fi
    echo_log "Removing stopped container - $NAME"
    exec_log docker rm $NAME;
  else
    echo_log "Container not found: $NAME"
  fi
}

function create_docker_network {
    echo_log "Creating Docker network \"$DOCKER_NETWORK\" if it does not exist."
    
    # Redirect stderr to stdout and suppress the output
    if docker network inspect $DOCKER_NETWORK &> /dev/null; then
        echo_log "Docker network \"$DOCKER_NETWORK\" already exists."
    else
        echo_log "Creating Docker network \"$DOCKER_NETWORK\"."
        exec_log docker network create --driver bridge $DOCKER_NETWORK
		echo_log "Docker network \"$DOCKER_NETWORK\" created."
    fi
}


#######################################
#       install functions
#######################################

function install_database {

	local CONTEXT="./Database"
	local DOCKER_COMPOSE_FILE="$CONTEXT/docker-compose-postgres.yml"
	local DOCKERFILE="$CONTEXT/postgres.dockerfile"
	local IMAGE_NAME="transcendence-postgres:latest"

	if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
		echo_log_exit "Docker compose file \"$DOCKER_COMPOSE_FILE\" does not exist."
	fi
	if [ ! -f "$DOCKERFILE" ]; then
		echo_log_exit "Dockerfile \"$DOCKERFILE\" does not exist."
	fi

    echo_log "Installing database"

	stop_and_rm_docker_container $DATABASE_CONTAINER_NAME

	build_docker_image $IMAGE_NAME $DOCKERFILE $CONTEXT

	echo_log "Database image built. Starting database container."

	exec_log docker-compose -f $DOCKER_COMPOSE_FILE --env-file $CONFIG_FILE up -d
}

function install_backend {

	local CONTEXT="./Backend"
	local DOCKER_COMPOSE_FILE="$CONTEXT/docker-compose-django.yml"
	local DOCKERFILE="$CONTEXT/django.dockerfile"
	local IMAGE_NAME="transcendence-django:latest"

	if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
		echo_log_exit "Docker compose file \"$DOCKER_COMPOSE_FILE\" does not exist."
	fi
	if [ ! -f "$DOCKERFILE" ]; then
		echo_log_exit "Dockerfile \"$DOCKERFILE\" does not exist."
	fi

	is_docker_container_running $DATABASE_CONTAINER_NAME
	if [ $? -ne 0 ]; then
		echo_log "Database container is not running. Installing database first."
		install_database
	fi

	stop_and_rm_docker_container $BACKEND_CONTAINER_NAME

    echo_log "Installing backend"

	build_docker_image $IMAGE_NAME $DOCKERFILE $CONTEXT

	echo_log "Backend image built. Starting backend container."

	exec_log docker-compose -f $DOCKER_COMPOSE_FILE --env-file $CONFIG_FILE up -d
}

function install_frontend {

	local CONTEXT="./Frontend"
	local DOCKER_COMPOSE_FILE="$CONTEXT/docker-compose-nginx.yml"
	local DOCKERFILE="$CONTEXT/nginx.dockerfile"
	local IMAGE_NAME="transcendence-nginx:latest"

	if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
		echo_log_exit "Docker compose file \"$DOCKER_COMPOSE_FILE\" does not exist."
	fi
	if [ ! -f "$DOCKERFILE" ]; then
		echo_log_exit "Dockerfile \"$DOCKERFILE\" does not exist."
	fi

	is_docker_container_running $BACKEND_CONTAINER_NAME
	if [ $? -ne 0 ]; then
		echo_log "Backend container is not running. Installing backend first."
		install_backend
	fi
	stop_and_rm_docker_container $FRONTEND_CONTAINER_NAME

    echo_log "Installing frontend"

	build_docker_image $IMAGE_NAME $DOCKERFILE $CONTEXT

	echo_log "Frontend image built. Starting frontend container."

	exec_log docker-compose -f $DOCKER_COMPOSE_FILE --env-file $CONFIG_FILE up -d
}

function install_targets {
	for target in "${TARGET_ENV[@]}"; do
		case $target in
			frontend) install_frontend && echo_log "${GR}Frontend installed succesfully${NC}";;
			backend) install_backend && echo_log "${GR}Backend installed succesfully${NC}";;
			database) install_database && echo_log "${GR}Database installed succesfully${NC}";;
			*)
				echo -e $RD"Argument \"$target\" must be one of the following: ${TARGET_LIST[*]}."
				echo -e "$USAGE"
				exit 1
				;;
		esac
	done

}

#######################################
#       Main Script
#######################################


check_cli_args "$@"
create_folder_if_not_exists $LOG_FOLDER
load_env_file $CONFIG_FILE
create_docker_network $DOCKER_NETWORK
install_targets