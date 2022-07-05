FROM python:3.10

COPY . /code
WORKDIR /code

RUN pip install -r requirements.txt
RUN python manage.py collectstatic

EXPOSE 8000

ENTRYPOINT [ "/bin/bash", "startup.sh" ]
