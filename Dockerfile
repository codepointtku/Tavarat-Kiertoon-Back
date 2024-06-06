FROM python:3.11
RUN apt-get update && apt-get install -y cron

WORKDIR /usr/src/app

COPY . .

# COPY ssl /etc/ssl

RUN pip install --no-cache-dir -r requirements.txt
RUN python manage.py makemigrations
RUN python manage.py collectstatic --noinput --clear