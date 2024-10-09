# MIS Server Core
> [!NOTE]
> The repository is not intended to be run in standalone! It has external dependencies so pls check this out [mis](https://github.com/mis-py/mis) for install and run instructions!

## Overview

Core capabilities:
- User management
- Group management
- Permissions
- Tasks and Jobs
- Modules
- Notifications

## Table of Contents

- [Contributing](#contributing)
- [License](#license)

## Supported env variables

| Variable name | Default Value | Description
| --- | --- | --- 
| TZ                          | Europe/Kyiv | Timezone for system operation and logs
| ENVIRONMENT                 | local | Set appropriate environment to run (local, dev, test, prod) 
| DEFAULT_ADMIN_PASSWORD      | admin | Password used to create 'admin' user while setup on clean database
| SECRET_KEY                  | secret_key | Seret key for token generation
| ALGORITHM                   | HS256 | Algorithm for token generation
| ACCESS_TOKEN_EXPIRE_MINUTES | 2880 | Token expiry time in minutes. set to 0 to never expire
| AUTHORIZATION_ENABLED       | true | In case of False all authorization creds will lead to admin user
| LOGGER_FORMAT               | \<green>{extra[datetime]}\</green> \<level>{level: <8}\</level> \<cyan>{name}\</cyan>:\<cyan>{function}\</cyan>:\<cyan>{line}</cyan> \<level>{message}\</level> | Logging for core and components
| LOG_ROTATION                | 00:00 | Log Rotation
| LOG_LEVEL                   | DEBUG | Log level
| ALLOW_ORIGINS               | - | For CORS manipulation. Not set by default
| ROOT_PATH                   | /api | Root path for all endpoints. use only with reverse proxy.
| DOCS_URL                    | /docs | Endpoint path for swagger
| OPEN_API_URL                | /openapi.json' | Endpoint for openapi.json file
| SERVER_HOST                 | localhost | Where to run uvicorn server
| SERVER_PORT                 | 8000 | Port for uvicorn server
| SERVER_LOG_LEVEL            | debug | Server log level

### Postgres connection settings
| Variable name | Default Value  | Description
| --- | --- | --- 
| POSTGRES_USER | postgres | Username to connect with
| POSTGRES_PASSWORD | postgres | Password to connect with
| POSTGRES_HOST | mis-postgres | Database instance hostname
| POSTGRES_PORT | 5432 | Database instance port
| POSTGRES_DB | mis | Database name to work with
| POSTGRES_CREATE_DB | False | Param used for tests

### Rabbit connection settings
| Variable name | Default Value  | Description
| --- | --- | --- 
| RABBITMQ_URI | amqp://guest:guest@mis-rabbitmq:5672/ | Rabbitmq uri to connect
| EVENTORY_LOG_LEVEL | INFO | Rabbitmq log level

### Redis connection settings
| Variable name | Default Value | Description
| --- | --- | --- 
| REDIS_URI | redis://mis-redis | Redis uri to connect

### Mongodb connection settings
| Variable name | Default Value | Description
| --- | --- | --- 
| MONGO_INITDB_ROOT_USERNAME | root      | Username to connect with
| MONGO_INITDB_ROOT_PASSWORD | root      | Password to connect with
| MONGO_INITDB_DATABASE      | mis       | Database name to work with
| MONGO_HOST                 | mis-mongo | Database instance hostname
| MONGO_PORT                 | 27017     | Database instance port


## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes.
4. Commit your changes: `git commit -m 'Add some feature'`.
5. Push to the branch: `git push origin feature-name`.
6. Open a pull request.

Please make sure your code adheres to the project's coding standards and passes tests before submitting a PR.

## License

This project is licensed under the  GNU GENERAL PUBLIC LICENSE - see the [LICENSE](LICENSE.txt) file for details.
