from pydantic_settings import BaseSettings, SettingsConfigDict
from const import ENV_FILE
from loguru import logger


class RabbitSettings(BaseSettings):
    RABBITMQ_URL: str = "amqp://guest:guest@rabbit:5672/"
    EVENTORY_LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )
