#!bin/bash

service cron start
python manage.py migrate
python manage.py createsuperuser --no-input
python manage.py runserver 0.0.0.0:9092 --noreload
