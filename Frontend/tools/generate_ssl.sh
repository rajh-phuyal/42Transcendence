#!/bin/sh

# Directories for your certificates
LOCAL_CRT_DIR="/etc/openssl"
LOCAL_CRT="$LOCAL_CRT_DIR/localhost.crt"
LOCAL_CSR="$LOCAL_CRT_DIR/localhost.csr"
LOCAL_KEY="$LOCAL_CRT_DIR/localhost.key"
CA_DIR="$LOCAL_CRT_DIR/ca"
CA_KEY="$CA_DIR/myCA.key"
CA_PEM="$CA_DIR/myCA.pem"
CA_SERIAL="$CA_DIR/myCA.srl"

# Domain details for the certificate
DOMAIN="localhost"
NAME="barelyalive"
IP_ADDRESS="127.0.0.1"

# Create directories for certificates
mkdir -p "$LOCAL_CRT_DIR" "$CA_DIR"

# Function to check if certificate is signed by CA
is_signed_by_ca() {
    # Check if certificate is signed by CA by inspecting its issuer
    openssl x509 -in "$LOCAL_CRT" -noout -issuer | grep -q "My CA"
    return $?
}

# Check if the certificate and key exist
if [ ! -f "$LOCAL_CRT" ] || [ ! -f "$LOCAL_KEY" ]; then
    echo "Generating SSL certificate..."

    if [ ! -f "$CA_PEM" ] || [ ! -f "$CA_KEY" ]; then
        # Create a Certificate Authority (CA) if it doesn't exist
        echo "Creating Certificate Authority..."
        
        # Generate the private key for the Certificate Authority (CA)
        openssl genrsa -out "$CA_KEY" 2048  # Removed passphrase
        openssl req -x509 -new -nodes -key "$CA_KEY" -sha256 -days 825 -out "$CA_PEM" -subj "/C=PT/ST=Lisbon/L=Lisbon/O=42Lisboa/CN=My CA"
        echo "Certificate Authority created."
    fi

    # Generate private key for the domain without passphrase
    openssl genrsa -out "$LOCAL_KEY" 2048  # Removed passphrase

    # Create a Certificate Signing Request (CSR)
    openssl req -new -key "$LOCAL_KEY" -out "$LOCAL_CSR" -subj "/C=PT/ST=Lisbon/L=Lisbon/O=42Lisboa/CN=$DOMAIN"

    # Generate config file for the certificate extensions (subjectAltName)
    >$LOCAL_CRT_DIR/$NAME.ext cat <<-EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names
[alt_names]
DNS.1 = $DOMAIN
DNS.2 = www.$DOMAIN
IP.1 = $IP_ADDRESS
EOF

    # Create the certificate (either self-signed or CA-signed)
    if [ -f "$CA_PEM" ] && [ -f "$CA_KEY" ]; then
        # Use the Certificate Authority to sign the certificate
        openssl x509 -req -in "$LOCAL_CSR" -CA "$CA_PEM" -CAkey "$CA_KEY" -CAcreateserial \
        -out "$LOCAL_CRT" -days 365 -sha256 -extfile "$LOCAL_CRT_DIR/$NAME.ext"  # Removed passphrase
        echo "CA-signed certificate generated."
    else
        # Self-signed certificate
        openssl x509 -req -days 365 -in "$LOCAL_CSR" -signkey "$LOCAL_KEY" -out "$LOCAL_CRT"  # Removed passphrase
        echo "Self-signed certificate generated."
    fi

    # Print the certificate
    cat "$LOCAL_CRT"

    echo "SSL certificate generation: DONE"

else
    echo "Using existing SSL certificate..."

    # Check if the certificate is signed by the CA
    if ! is_signed_by_ca; then
        echo "The certificate is self-signed, signing it with the CA..."
        
        # Sign the existing certificate with the CA
        openssl x509 -req -in "$LOCAL_CSR" -CA "$CA_PEM" -CAkey "$CA_KEY" -CAcreateserial \
        -out "$LOCAL_CRT" -days 365 -sha256 -extfile "$LOCAL_CRT_DIR/$NAME.ext"  # Removed passphrase
        echo "Certificate signed by the CA."
    else
        echo "The certificate is already signed by the CA."
    fi
fi

# Output the generated paths for entrypoint.sh
export "FILE_CRT=$LOCAL_CRT"
export "FILE_KEY=$LOCAL_KEY"
