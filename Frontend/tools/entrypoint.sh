#!/bin/sh
set -e

# Check if environment is production or local
if [ "$LOCAL_DEPLOY" == TRUE ]; then
    echo "Starting in local mode..."
    . /tools/generate_ssl.sh
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
      echo "Error: Required .crt or .key file not found in $SSL_DIR"
          exit 1
    fi
fi

export FILE_CRT FILE_KEY DOMAIN_NAMES
export DOMAIN_NAMES_SPACED=$(echo $DOMAIN_NAMES | sed 's/,/ /g')
echo "Update the configuration by expanding..."
echo -e '\t"FILE_CRT"='"$FILE_CRT"
echo -e '\t"FILE_KEY"='"$FILE_KEY"
echo -e '\t"DOMAIN_NAMES_SPACED"='"$DOMAIN_NAMES_SPACED"
envsubst '${FILE_CRT} ${FILE_KEY} ${DOMAIN_NAMES_SPACED}' < "/etc/nginx/nginx.conf" > "/etc/nginx/nginx.temp.conf"
mv "/etc/nginx/nginx.temp.conf" "/etc/nginx/nginx.conf"
echo "Substituted environment variables in /etc/nginx/nginx.conf"

# Start NGINX
echo "Starting NGINX..."
nginx -g 'daemon off;'
