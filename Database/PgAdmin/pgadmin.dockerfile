# astein: This dockerfile will be used from the main docker-compose file
# Start with the official pgAdmin image
FROM dpage/pgadmin4:latest

# Switch to root user
USER root

# curl for the healthcheck
# envsubst (gettext package) for env var expanision in config files
RUN apk --no-cache add curl gettext postgresql-client

# Define build arguments will be set in the docker-compose file
ARG PA_DB_NAME
ARG PA_DB_PORT
ARG PA_DB_USER
ARG PA_DB_PSWD

# Copy the necessary files into the container
COPY ./config/servers.json /pgadmin4/servers.json
COPY ./config/.pgpass /root/.pgpass
# Substitute environment variables in the files
# Substitute environment variables in the files and save them back to the original location
RUN echo "Port: ${PA_DB_PORT}, DB Name: ${PA_DB_NAME}, User: ${PA_DB_USER}" && \
	envsubst < /pgadmin4/servers.json > /pgadmin4/servers.json.expanded && \
	mv /pgadmin4/servers.json.expanded /pgadmin4/servers.json && \
	envsubst < /root/.pgpass > /root/.pgpass.expanded && \
	mv /root/.pgpass.expanded /root/.pgpass

# Ensure the .pgpass file has the correct permissions
RUN chmod 600 /root/.pgpass

# Create tools directory
RUN mkdir -p /tools

# Copy the entrypoint script
COPY ./tools/entrypoint.sh /tools/entrypoint.sh
RUN chmod +x /tools/entrypoint.sh

# Copy healthcheck script
COPY ./tools/healthcheck.sh /tools/healthcheck.sh
RUN chmod +x /tools/healthcheck.sh

# Expose the default pgAdmin port
EXPOSE 80
USER pgadmin

# Start pgAdmin
CMD ["/tools/entrypoint.sh"]