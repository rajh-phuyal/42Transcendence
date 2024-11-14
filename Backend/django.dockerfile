# astein: This dockerfile will be used from the main docker-compose file
# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=app.settings

# Changing the working directory (cd)
WORKDIR /app

# COPY src /app/ we might need it for later when the project is ready for submission

# We need the requirements file during the buildng phase of the image,
# so we copy it and remove it after the requirements are installed.
# This is necessary because the volume is not moynted during the build time yet
RUN mkdir /tempReqBuild/
COPY ./src/requirements.txt /tempReqBuild/requirements.txt
RUN pip install -r /tempReqBuild/requirements.txt
RUN rm -rf /tempReqBuild/

EXPOSE 8000

# Copy the entrypoint.sh, make it excutable and run it
COPY ./tools/entrypoint.sh /tools/entrypoint.sh
RUN chmod +x /tools/entrypoint.sh
ENTRYPOINT ["/tools/entrypoint.sh"]

# Run the application
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Run with ASGI server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "app.asgi:application"]
