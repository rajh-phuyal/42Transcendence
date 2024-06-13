#!/bin/bash

# This script is used to deploy the application to a target environment.

set -euo pipefail
RD='\033[0;31m'
YL='\033[0;33m'
GR='\033[0;32m'
NC='\033[0m'

TARGET_LIST=("frontend" "backend" "database")
LOG_FOLDER="Logs"
LOG_FILE="$LOG_FOLDER/deploy.log"
USAGE=$YL"Usage: ./deploy.sh [OPTIONS]
Options:
    -h | --help      Display this message
    -t | --target    Service to be installed. (default: all || ${TARGET_LIST[*]})
    -c | --conf      Relative path to the .env file"$NC

#######################################
#	   Utility functions
#######################################

function echo_log { 
  echo -e "$(date +%Y%m%d.%H%M%S): ${@:-NO_MESSAGE_SUPPLIED} ${NC}" 2>&1 | tee -a $LOG_FILE
}

function echo_log_exit {
  echo_log "${RD}ERROR - ${@:-NO_MESSAGE_SUPPLIED}" 
  exit 1
}

function exec_log {
  PARAMS="$@"
  echo -e "$(date +%Y%m%d.%H%M%S): ${GR} $PARAMS" ${NC} 2>&1 | tee -a $LOG_FILE
  eval $PARAMS 2>&1 | tee -a $LOG_FILE
}

function check_cli_args {

TARGET_ENV=()
	if [ "$#" -eq 0 ]; then
		echo -e $RD"Error: No arguments provided."$NC
		echo -e "$USAGE"
		exit 1
	fi

    while [ "$#" -gt 0 ]; do
        case "$1" in
            -h|--help)
                echo -e "$USAGE"
                exit 0
                ;;
            -t|--target)
                if [ -n "${2-}" ]; then
                    TARGET_ENV+=("$2")
                    shift 2
                else
                    echo -e $RD"Error: Missing value for the target option $1 $NC"
                    echo -e "$USAGE"
                    exit 1
                fi
                ;;
            -c|--conf)
                if [ -n "${2-}" ]; then
                    CONFIG_FILE="$2"
                    shift 2
                else
                    echo -e $RD"ERROR: Missing value for the config option $1 $NC"
                    echo -e "$USAGE"
                    exit 1
                fi
                ;;
            *)
                echo -e $RD"ERROR: Invalid option $1 $NC"
                echo -e "$USAGE"
                exit 1
                ;;
        esac
    done

if [ ${#TARGET_ENV[@]} -eq 0 ]; then
    echo -e $GR"Target not specified. Installing all targets: ${TARGET_LIST[*]} $NC"
    TARGET_ENV=("${TARGET_LIST[@]}")
fi

if [ -z "${CONFIG_FILE:-}" ]; then
    echo -e $RD".env file must be specified. $NC"
    echo -e "$USAGE"
    exit 1
fi

}

function  create_folder_if_not_exists() {
    local folder_path="$1"
    if [ ! -d "$folder_path" ]; then
        mkdir -p "$folder_path"
        echo_log "Folder does not exist. Creating \"$folder_path\""
    fi
}

function load_env_file {
	local env_file="$1"
	if [ -f "$env_file" ]; then
		source "$env_file"
		echo_log "Loading environment variables from \"$env_file\""
	else
		echo_log_exit "Environment file \"$env_file\" does not exist."
	fi
}

function build_docker_image {
  # $1 Docker image name
  # $2 Dockerfile path
  # $3 Docker build context
  # $4 Docker build args
  # $5 Docker build target
  # $6 Docker build tag
  local NAME=${1}
  local DOCKERFILE=${2}
  local CONTEXT=${3}
  local BUILD_ARGS=${4}
  local TARGET=${5}
  local TAG=${6}
  echo_log "Building Docker image - $NAME"
  exec_log docker build -f $DOCKERFILE -t $TAG $BUILD_ARGS $TARGET $CONTEXT
}


function stop_docker_container {
  # $1 Docker container name
  local NAME=${1}
  if [ "$(docker ps -qa -f name=$NAME)" ]; then # Check if container exists
    echo_log "Found container - $NAME"
    if [ "$(docker ps -q -f name=$NAME)" ]; then # Check if container is running
        echo_log "Stopping running container - $NAME"
        exec_log docker stop $NAME;
    fi
    echo_log "Removing stopped container - $NAME"
    exec_log docker rm $NAME;
  else
    echo_log "Container not found - $NAME"
  fi
}

function create_docker_network {
  # Create default network if it doesn't exist
  local DOCKER_NETWORK=${1}
  if [ -z "$DOCKER_NETWORK" ]; then
	echo_log_exit "Docker network not specified."
  fi
	docker network inspect ${DOCKER_NETWORK} > /dev/null 2>&1
	if [ $? != 0 ]; then
		docker network create --driver bridge ${DOCKER_NETWORK}
	fi
}

#######################################
#       install functions
#######################################

function install_database {
    echo_log "Installing database"
	# Install database
	echo_log "Database installation complete"
}

function install_backend {
    echo_log "Installing backend"
	# Install backend
	echo_log "Backend installation complete"
}

function install_frontend {
    echo_log "Installing frontend"
	local DOCKER_COMPOSE_FILE="./docker/requirements/service-frontend/docker-compose-nginx.yml"
	local DOCKERFILE="./docker/requirements/service-frontend/nginx.dockerfile"
	# Install frontend
	exec_log docker-compose -f docker-compose.yml --env-file $CONFIG_FILE up -d
	echo_log "Frontend installation complete"
}

function install_targets {
	for target in "${TARGET_ENV[@]}"; do
		case $target in
			frontend) install_frontend ;;
			backend) install_backend ;;
			database) install_database ;;
			*)
				echo_log_exit "Argument \"$target\" must be one of the following: ${TARGET_LIST[*]}."
				;;
		esac
	done

}

#######################################
#       Main Script
#######################################

check_cli_args "$@"

load_env_file $CONFIG_FILE
create_folder_if_not_exists $LOG_FOLDER
create_docker_network $DOCKER_NETWORK

install_targets