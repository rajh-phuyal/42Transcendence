#!/bin/sh

LOCAL_CRT_DIR="/etc/openssl/"
LOCAL_CSR="$LOCAL_CRT_DIR""localhost.csr"
FILE_KEY="$LOCAL_CRT_DIR""localhost.key"
FILE_CRT="$LOCAL_CRT_DIR""localhost.crt"
if [ ! -f "$LOCAL_CRT" ] || [ ! -f "$FILE_KEY" ]; then
    echo "Generating self-signed SSL certificate..."
    mkdir -p "$LOCAL_CRT_DIR"
    openssl genrsa -out "$FILE_KEY" 2048
    openssl req -new -key "$FILE_KEY" -out "$LOCAL_CSR" -subj "/C=PT/ST=Lisbon/L=Lisbon/O=42Lisboa/CN=ahok.cool"
    openssl x509 -req -days 365 -in "$LOCAL_CSR" -signkey "$FILE_KEY" -out "$FILE_CRT"
	echo "Generating self-signed SSL certificate...DONE"
else
    echo "Using existing self-signed SSL certificate..."
fi

# Output the generated paths for entrypoint.sh
export "FILE_CRT=$FILE_CRT"
export "FILE_KEY=$FILE_KEY"
