from pydantic_settings import BaseSettings


class CoreSettings(BaseSettings):
    DEFAULT_ADMIN_PASSWORD: str = "admin"

    SECRET_KEY: str = "secret_key"
    ALGORITHM: str = "HS256"

    # 60 minutes * 24 hours * 2 days = 2 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 2

    AUTHORIZATION_ENABLED: bool = False

    # HOSTS_WHITELIST: list = [
    #     "167.235.28.217"  # CRM (leads)
    # ]
    #
    # NETWORKS_WHITELIST = [
    #     "91.108.6.0/24",
    #     # "10.0.0.0/18",
    # ]

    # settings for ModuleLogs component
    LOGGER_FORMAT: str = (
        "<green>{extra[datetime]}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<magenta>{extra[context_key]}</magenta> | "
        "<level>{message}</level>"
    )
    LOG_ROTATION: str = "00:00"
    LOG_LEVEL: str = "DEBUG"

    ALLOW_ORIGINS: str = "http://localhost:9090"

    ROOT_PATH: str = "/api"
    DOCS_URL: str = '/docs'
    OPEN_API_URL: str = '/openapi.json'

    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 8000
    SERVER_LOG_LEVEL: str = "debug"

