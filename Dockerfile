FROM python:3.12-alpine

RUN apk add --update --no-cache curl

COPY ./start.sh .
RUN chmod +x /start.sh

RUN curl https://letsencrypt.org/certs/lets-encrypt-r3.pem -o /usr/local/share/ca-certificates/R3.crt
RUN curl https://letsencrypt.org/certs/2024/e5.pem -o /usr/local/share/ca-certificates/e5.crt
RUN curl https://letsencrypt.org/certs/2024/e6.pem -o /usr/local/share/ca-certificates/e6.crt
RUN curl https://letsencrypt.org/certs/2024/r10.pem -o /usr/local/share/ca-certificates/r10.crt
RUN curl https://letsencrypt.org/certs/2024/r11.pem -o /usr/local/share/ca-certificates/r11.crt
RUN curl https://letsencrypt.org/certs/2024/e7.pem -o /usr/local/share/ca-certificates/e7.crt
RUN curl https://letsencrypt.org/certs/2024/e8.pem -o /usr/local/share/ca-certificates/e8.crt
RUN curl https://letsencrypt.org/certs/2024/e9.pem -o /usr/local/share/ca-certificates/e9.crt
RUN curl https://letsencrypt.org/certs/2024/r12.pem -o /usr/local/share/ca-certificates/r12.crt
RUN curl https://letsencrypt.org/certs/2024/r13.pem -o /usr/local/share/ca-certificates/r13.crt
RUN curl https://letsencrypt.org/certs/2024/r14.pem -o /usr/local/share/ca-certificates/r14.crt
RUN update-ca-certificates

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./*.py /app/
COPY ./libs /app/libs
COPY ./core /app/core
COPY ./modules /app/modules

ENV PYTHONPATH=/app

EXPOSE 80

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]