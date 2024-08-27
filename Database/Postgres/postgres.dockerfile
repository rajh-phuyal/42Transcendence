# astein: This dockerfile will be used from the main docker-compose file
FROM postgres:16-alpine

# Set the default encoding to UTF-8
ENV LANG C.UTF-8
# Set the default timezone to UTC
ENV TZ UTC

# Install envsubst (part of gettext)
RUN apk add --no-cache gettext

# Copy the initialization scripts into the image
# All those Scripts will be executed in alphabetical order when the container starts
COPY ./init-db /docker-entrypoint-initdb.d/

# Copy the custom entrypoint script and make it executable
COPY ./tools/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set the custom entrypoint script as the default entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Expose the default PostgreSQL port
EXPOSE 5432

# Start the PostgreSQL server
CMD ["postgres"]