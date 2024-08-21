# Start with the official pgAdmin image
FROM dpage/pgadmin4:latest

# Copy the necessary files into the container
COPY ./pgadmin/servers.json /pgadmin4/servers.json
COPY ./pgadmin/.pgpass /pgpassfile
RUN chmod 600 /pgadmin4/servers.json /pgpassfile

# Expose the default pgAdmin port
EXPOSE 80

# Start pgAdmin
CMD ["/entrypoint.sh"]
