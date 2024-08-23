# astein: This dockerfile will be used from the main docker-compose file
# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY src/requirements.txt /app/
RUN pip install -r requirements.txt

EXPOSE 8000

# Copy the project code into the container
COPY src /app/

# Set the working directory to where manage.py is located
WORKDIR /app

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
