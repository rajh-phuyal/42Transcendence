# astein: This dockerfile will be used from the main docker-compose file
FROM postgres:17.4-bullseye

# Set the default encoding to UTF-8
ENV LANG C.UTF-8
# Set the default timezone to UTC
ENV TZ UTC

# Install envsubst (part of gettext)
RUN apt-get update && apt-get install -y gettext && rm -rf /var/lib/apt/lists/*

# Create a new group and user to match the host GID for the mounted volume
# ALPINE:
# RUN addgroup -g 1024 pg_group && adduser postgres pg_group

# With this cmd on the host u can double check that it workded:
#  docker exec -it db sh -c "id postgres"
#   ->> "uid=70(postgres) gid=70(postgres) groups=70(postgres),70(postgres),1024(pg_group)"

# Copy the initialization scripts into the image
# All those Scripts will be executed in alphabetical order when the container starts
COPY ./init-db /docker-entrypoint-initdb.d/

# Make a directory for the tools
RUN mkdir -p /tools
RUN chown -R postgres:postgres /tools

# Copy the custom entrypoint script and make it executable
COPY ./tools/entrypoint.sh /tools/entrypoint.sh
RUN chmod +x /tools/entrypoint.sh
# Copy the root user accounts script and make it executable
COPY ./tools/root_accounts.sh /tools/root_accounts.sh
RUN chmod +x /tools/root_accounts.sh
# Copy the dummy data script and make it executable
COPY ./tools/create_dummy.sh /tools/create_dummy.sh
RUN chmod +x /tools/create_dummy.sh
# Expose the default PostgreSQL port
EXPOSE 5432

# Set the custom entrypoint script as the default entrypoint
ENTRYPOINT ["/tools/entrypoint.sh"]

# Start the PostgreSQL server
CMD ["postgres"]