# astein: This dockerfile will be used from the main docker-compose file
# Use an official Python runtime as a parent image
FROM python:3.10
RUN apt-get update && apt-get install -y gettext && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=app.settings
ENV PYTHONPATH=/Backend/src 

# Make media directory
RUN mkdir -p /$MEDIA_VOLUME_NAME/

# Changing the working directory (cd)
WORKDIR /app

# COPY src /app/ we might need it for later when the project is ready for submission

# We need the requirements file during the buildng phase of the image,
# so we copy it and remove it after the requirements are installed.
# This is necessary because the volume is not mounted during the build time yet
RUN mkdir /tempReqBuild/
COPY ./src/requirements.txt /tempReqBuild/requirements.txt
RUN pip install -r /tempReqBuild/requirements.txt
RUN rm -rf /tempReqBuild/

# Copy the entrypoint.sh, make it excutable and run it
WORKDIR /
RUN mkdir -p /tools
COPY ./tools/entrypoint.sh /tools/entrypoint.sh
RUN chmod +x /tools/entrypoint.sh

# make migrations and generate language files on the entrypoint
ENTRYPOINT ["/tools/entrypoint.sh"]

EXPOSE 8000

# Run with ASGI server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "app.asgi:application"]
