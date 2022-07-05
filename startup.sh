#!bin/bash

python manage.py migrate
python manage.py createsuperuser --no-input
python manage.py runserver 0.0.0.0:9092