# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

COPY src /app/

RUN pip install -r requirements.txt

EXPOSE 8000

# Copy the project code into the container

# Set the working directory to where manage.py is located
WORKDIR /app

RUN python manage.py migrate
RUN python manage.py makemigrations

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]