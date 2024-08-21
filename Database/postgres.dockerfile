FROM postgres:16-alpine

# Set the default encoding to UTF-8
ENV LANG C.UTF-8

# Set the default timezone to UTC
ENV TZ UTC

# Expose the default PostgreSQL port
EXPOSE 5432

# Start the PostgreSQL server
CMD ["postgres"]
