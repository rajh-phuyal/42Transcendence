# astein: This dockerfile will be used from the main docker-compose file
# Stage 1: Use an intermediary image to process the files
FROM alpine as intermediary

# curl for the healthcheck
# envsubst (gettext package) for env var expanision in config files
RUN apk --no-cache add curl gettext

# Copy the necessary files into the container and make them excutable
COPY ./config/.pgpass /tmp/.pgpass
COPY ./config/servers.json /tmp/servers.json

# Substitute environment variables in the files
RUN envsubst < /tmp/.pgpass > /tmp/.pgpass.expanded && \
    envsubst < /tmp/servers.json > /tmp/servers.json.expanded

# Stage 2: Build the final image
FROM dpage/pgadmin4:8.11.0


# Copy the expanded files from the intermediary container
COPY --from=intermediary /tmp/.pgpass.expanded /.pgpass
COPY --from=intermediary /tmp/servers.json.expanded /pgadmin4/servers.json

# Ensure the pgpass file has the correct permissions
USER root
# Ensure correct ownership of the pgAdmin volume
RUN chown -R 5050:5050 /var/lib/pgadmin
RUN chmod -R 755 /var/lib/pgadmin
RUN chmod 600 /.pgpass
USER pgadmin

# Expose the default pgAdmin port
EXPOSE 80

# Start pgAdmin
ENTRYPOINT ["/entrypoint.sh"]
