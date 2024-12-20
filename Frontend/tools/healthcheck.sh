# healthcheck.sh
#!/bin/bash

if [ -z "$DOMAIN_NAMES" ]; then
  echo "DOMAIN_NAMES is not set"
  exit 1
fi

# The insecure flag is used to allow curl to make requests to self-signed certificates
if LOCAL_DEPLOY=TRUE; then
  INSECURE_FLAG="--insecure"
else
  INSECURE_FLAG=""
fi

for domain in ${DOMAIN_NAMES//,/ }; do
  if [ -n "$domain" ]; then
    # Check if online and the website redirects from HTTP to HTTPS correctly
    curl -f $INSECURE_FLAG -L "http://$domain/" || exit 1          # Should follow the redirect to HTTPS
    curl -f $INSECURE_FLAG -L "http://$domain:80/" || exit 1        # Check for redirect on port 80
    curl -f $INSECURE_FLAG "https://$domain:443/" || exit 1        # Check the HTTPS site directly
  fi
done

echo "Healthcheck passed"