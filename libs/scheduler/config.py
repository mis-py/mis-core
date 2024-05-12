from pydantic_settings import BaseSettings, SettingsConfigDict
from const import ENV_FILE


class SchedulerSettings(BaseSettings):
    REDIS_HOST: str = "redis"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) + '.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )
