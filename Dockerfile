FROM python:3.11
RUN apt-get update && apt-get install -y cron

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN python manage.py makemigrations
RUN python manage.py migrate
entrypoint service cron start; python manage.py crontab add; python manage.py runserver 0.0.0.0:8000