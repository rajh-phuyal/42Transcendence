FROM python:3.12-alpine

 # Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# This is to prevent Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED 1 

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "your_project.wsgi:application"]
