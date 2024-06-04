[TBW]!!!

How to build image for mis-project-api:

`poetry export --without-hashes --format=requirements.txt > requirements.txt`

then

`docker build . -t mis:<version>`

docker-compose.yml example:

```
mis-project-api:
  container_name: mis-project-api
  build: mis-project-api/
  volumes:
    - "/etc/timezone:/etc/timezone:ro"
    - "/etc/localtime:/etc/localtime:ro"
  networks:
    - mis-net
  environment:
    - VIRTUAL_HOST=${HOST_URL}
    - LETSENCRYPT_HOST=${HOST_URL}
    - VIRTUAL_PATH=${API_PATH}
    - VIRTUAL_DEST=${API_DEST}      
    - ENVIRONMENT=${ENVIRONMENT}
    - LOG_LEVEL=${LOG_LEVEL}
    - DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}
    - POSTGRES_USER=${POSTGRES_USER}
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    - POSTGRES_HOST=${POSTGRES_HOST}
    - POSTGRES_PORT=${POSTGRES_PORT}
    - POSTGRES_DB=${POSTGRES_DB}
    - RABBITMQ_URL=${RABBITMQ_URL}
    - EVENTORY_LOG_LEVEL=${EVENTORY_LOG_LEVEL}
    - REDIS_HOST=${REDIS_HOST}
    - MONGODB_URI=${MONGODB_URI}
    - MONGODB_TABLE=${MONGODB_TABLE}
    - TIMEZONE=${TIMEZONE}
    
    - MAX_WORKERS=1
  depends_on:
    redis:
      condition: service_healthy
    postgres:
      condition: service_healthy
    rabbit:
      condition: service_healthy
    mongodb:
      condition: service_healthy
  restart: unless-stopped
```
