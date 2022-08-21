FROM python:3.10

COPY . /code
WORKDIR /code

RUN apt-get update && apt-get -y install cron

RUN pip install -r requirements.txt
RUN python manage.py collectstatic

EXPOSE 9092

ENTRYPOINT [ "/bin/bash", "startup.sh" ]
