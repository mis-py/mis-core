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

| Variable name | Default Value | Required | Description
| --- | --- | --- | --- 
| TIMEZONE                    | Europe/Kyiv | No | Timezone for system operation and logs |
| DEFAULT_ADMIN_PASSWORD      | admin | No | Password used to create 'admin' user while setup on clean database
| SECRET_KEY                  | wherysecretkey | No | Seret key for token generation
| ALGORITHM                   | HS256 | No | Algorithm for token generation
| ACCESS_TOKEN_EXPIRE_MINUTES | 2880 | No | Token expiry time in minutes. set to 0 to never expire
| AUTHORIZATION_ENABLED       | true | No | In case of False all authorization creds will lead to admin user
| LOGGER_FORMAT               | \<green>{extra[datetime]}\</green> \<level>{level: <8}\</level> \<cyan>{name}\</cyan>:\<cyan>{function}\</cyan>:\<cyan>{line}</cyan> \<level>{message}\</level> | No | Logging for core and components |
| LOG_ROTATION                | 00:00 | No | Log Rotation
| LOG_LEVEL                   | DEBUG | No | Log level
| ROOT_PATH                   | /api | No | Root path for all endpoints. use only with reverse proxy.
| DOCS_URL                    | /docs | No | Endpoint path for swagger
| OPEN_API_URL                | /openapi.json' | No | Endpoint for openapi.json file
| ALLOW_ORIGINS               | http://localhost:9090 | No | For CORS manipulation

### Postgres connection settings
| Variable name | Default Value | Required | Description
| --- | --- | --- | --- 
| POSTGRES_USER | postgres | |
| POSTGRES_PASSWORD | postgres | |
| POSTGRES_HOST | postgres | |
| POSTGRES_PORT | 5432 | |
| POSTGRES_DB | mis | |

### Rabbit connection settings
| Variable name | Default Value | Required | Description
| --- | --- | --- | --- 
| RABBITMQ_URL | amqp://guest:guest@tabbitmq:5672/ | |
| EVENTORY_LOG_LEVEL | INFO | |

### Redis connection settings
| Variable name | Default Value | Required | Description
| --- | --- | --- | --- 
| REDIS_HOST | redis | No | Redis hostname


### Mongodb connection settings
| Variable name | Default Value | Required | Description
| --- | --- | --- | --- 
| MONGODB_URI | mongodb://root:root@mongodb:27017/ | |
| MONGODB_TABLE | mis | |
### Unicorn server settings
| Variable name | Default Value | Required | Description
| --- | --- | --- | --- 
| SERVER_HOST | localhost | No | Hostname
| SERVER_PORT | 8000 | No | Port 
| SERVER_LOG_LEVEL | debug | No | Log level


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
