# healthcheck.sh
#!/bin/bash
pg_isready -h db || exit 1