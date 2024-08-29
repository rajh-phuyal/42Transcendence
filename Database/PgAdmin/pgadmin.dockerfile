# astein: This dockerfile will be used from the main docker-compose file
# Start with the official pgAdmin image
FROM dpage/pgadmin4:latest

# Switch to root user
USER root

# curl for the healthcheck
# envsubst (gettext package) for env var expanision in config files
RUN apk --no-cache add curl gettext

# Define build arguments
ARG PA_DB_PORT
ARG PA_DB_NAME
ARG PA_DB_USER

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

USER pgadmin

# Expose the default pgAdmin port
EXPOSE 80

# Start pgAdmin
CMD ["/entrypoint.sh"]