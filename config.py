from pydantic_settings import BaseSettings, SettingsConfigDict
from const import ENV_FILE


class CoreSettings(BaseSettings):
    URL_ROOT_PATH: str = "/api"

    DEFAULT_ADMIN_PASSWORD: str = "admin"

    # SECRET_KEY: str = secrets.token_urlsafe(32)
    SECRET_KEY: str = "wherysecretshlyapa"
    ALGORITHM: str = "HS256"

    # 60 minutes * 24 hours * 2 days = 2 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 2

    # GIT_API_TOKEN: str = ""

    AUTHORIZATION_ENABLED: bool = False

    # TODO reintroduce it properly
    # HOSTS_WHITELIST: list = [
    #     "167.235.28.217"  # CRM (leads)
    # ]
    #
    # NETWORKS_WHITELIST = [
    #     "91.108.6.0/24",
    #     # "10.0.0.0/18",
    # ]

    # ENVIRONMENT: str = os.getenv('ENVIRONMENT', DEV_ENVIRONMENT)

    # settings for ModuleLogs component
    LOGGER_FORMAT: str = (
        "<green>{extra[datetime]}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    LOG_ROTATION: str = "00:00"
    LOG_LEVEL: str = "DEBUG"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) + '.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )
