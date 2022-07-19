#!bin/bash

SUBSCRIBER_MODE=OFF python manage.py migrate
SUBSCRIBER_MODE=OFF python manage.py createsuperuser --no-input
python manage.py runserver 0.0.0.0:9092
