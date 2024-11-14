#!/bin/sh

# Set certificate and configuration paths
FILE_KEY=""
FILE_CRT=""

# Check if environment is production or local
if [ "$LOCAL_DEPLOY" == TRUE]; then
	echo "Starting in local mode..."
	FILE_CRT_DIR="/etc/openssl/"
	LOCAL_CSR="$LOCAL_CRT_DIR""localhost.csr"
	FILE_KEY="$LOCAL_CRT_DIR""localhost.key"
	FILE_CRT="$LOCAL_CRT_DIR""localhost.crt"
    if [ ! -f "$LOCAL_CRT" ] || [ ! -f "$FILE_KEY" ]; then
        echo "Generating self-signed SSL certificate..."
        mkdir -p "$LOCAL_CRT_DIR"
        openssl genrsa -out "$FILE_KEY" 2048
        openssl req -new -key "$FILE_KEY" -out "$LOCAL_CSR" -subj "/C=PT/ST=Lisbon/L=Lisbon/O=42Lisboa/CN=ahok.cool"
        openssl x509 -req -days 365 -in "$LOCAL_CSR" -signkey "$FILE_KEY" -out "$FILE_CRT"
		cat $FILE_CRT
		echo "Generating self-signed SSL certificate...DONE"
    else
        echo "Using existing self-signed SSL certificate..."
    fi
    # Use LOCAL configuration
    cp "/tmp/nginx/nginx_local.conf" /etc/nginx/nginx.conf
else
	echo "Starting in production mode..."
	echo "Searching for ssl files..."
	# This is set by the docker compose prod volume section
	SSL_DIR="/etc/ssl/privatessl"
	# Find the first .cer file and assign it to FILE_CRT
	FILE_CRT=$(find "$SSL_DIR" -type f -name "*.crt" | head -n 1)
	# Find the first .key file and assign it to FILE_KEY
	FILE_KEY=$(find "$SSL_DIR" -type f -name "*.key" | head -n 1)
	echo "Using Certificate File: $FILE_CRT"
	echo "Using Key File: $FILE_KEY"
	if [[ -z "$FILE_CRT" || -z "$FILE_KEY" ]]; then
	  echo "Error: Required .cer or .key file not found in $SSL_DIR"
  		exit 1
	fi

	# Use PRODUCTION configuration
    cp "/tmp/nginx/nginx_production.conf" /etc/nginx/nginx.conf

fi

export FILE_CRT FILE_KEY DOMAIN_NAME
echo "Update the configuration by expanding..."
echo '\t"FILE_CRT"='"$FILE_CRT"
echo '\t"FILE_KEY"='"$FILE_KEY"
echo '\t"DOMAIN_NAME"='"$DOMAIN_NAME"
envsubst < "/etc/nginx/nginx.conf" > "/etc/nginx/nginx.conf"
echo "Substituted environment variables in /etc/nginx/nginx.conf"

# Start NGINX
nginx -g 'daemon off;'
