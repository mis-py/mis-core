FROM python:3.12

COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/gunicorn_conf.py /gunicorn_conf.py

COPY ./docker/start-reload.sh /start-reload.sh

RUN chmod +x /start-reload.sh

RUN mkdir ./app/
RUN mkdir ./app/env_override

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