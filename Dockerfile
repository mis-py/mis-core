FROM python:3.12

RUN apt-get -y update; apt-get -y install curl

COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/gunicorn_conf.py /gunicorn_conf.py

COPY ./docker/start-reload.sh /start-reload.sh

RUN chmod +x /start-reload.sh

RUN mkdir ./app/
RUN mkdir ./app/env_override

RUN curl https://letsencrypt.org/certs/lets-encrypt-r3.pem -o /usr/local/share/ca-certificates/R3.crt
RUN update-ca-certificates

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./*.py /app/
COPY ./libs /app/libs
COPY ./core /app/core
COPY ./modules /app/modules

WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 80

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]