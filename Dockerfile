FROM python:3.11
RUN apt-get update && apt-get install -y cron

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN python manage.py makemigrations
