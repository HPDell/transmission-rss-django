FROM python:3.10

RUN apt-get update && apt-get -y install cron

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY . /code
WORKDIR /code

RUN python manage.py collectstatic

EXPOSE 9092

ENTRYPOINT [ "/bin/bash", "startup.sh" ]
