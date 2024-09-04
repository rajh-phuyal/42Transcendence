# astein: This dockerfile will be used from the main docker-compose file
# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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

# make migrations on the entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]