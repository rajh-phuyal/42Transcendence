# astein: This dockerfile will be used from the main docker-compose file
# Start with the official pgAdmin image
FROM dpage/pgadmin4:latest

# Switch to root user
USER root

RUN apk --no-cache add curl

# Copy the necessary files into the container
COPY ./config/servers.json /pgadmin4/servers.json
COPY ./config/.pgpass /pgpassfile
RUN chmod 600 /pgadmin4/servers.json /pgpassfile

USER pgadmin

# Expose the default pgAdmin port
EXPOSE 80

# Start pgAdmin
CMD ["/entrypoint.sh"]
