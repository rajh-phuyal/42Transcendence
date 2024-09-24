# astein: This dockerfile will be used from the main docker-compose file
FROM postgres:16-alpine

# Set the default encoding to UTF-8
ENV LANG C.UTF-8
# Set the default timezone to UTC
ENV TZ UTC

# Install envsubst (part of gettext)
RUN apk add --no-cache gettext

# Create a new group and user to match the host GID for the mounted volume
RUN addgroup -g 1024 pg_group && adduser postgres pg_group
# With this cmd on the host u can double check that it workded:
#  docker exec -it db sh -c "id postgres"
#   ->> "uid=70(postgres) gid=70(postgres) groups=70(postgres),70(postgres),1024(pg_group)"

# Copy the initialization scripts into the image
# All those Scripts will be executed in alphabetical order when the container starts
COPY ./init-db /docker-entrypoint-initdb.d/

# Copy the custom entrypoint script and make it executable
COPY ./tools/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Copy the dummy data script
COPY ./tools/create_dummy.sh /usr/local/bin/create_dummy.sh
COPY ./tools/create_dummy.sql /usr/local/bin/create_dummy.sql

# Set the custom entrypoint script as the default entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Expose the default PostgreSQL port
EXPOSE 5432

# Start the PostgreSQL server
CMD ["postgres"]