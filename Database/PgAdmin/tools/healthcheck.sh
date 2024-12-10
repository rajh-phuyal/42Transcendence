# healthcheck.sh
#!/bin/bash

if [ -z "$DOMAIN_NAMES" ]; then
  echo "DOMAIN_NAMES is not set"
  exit 1
fi

for domain in ${DOMAIN_NAMES//,/ }; do
  if [ -n "$domain" ]; then
    curl -f "http://$domain:80/" || exit 1
  fi
done

echo "Healthcheck passed"