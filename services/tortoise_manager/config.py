from pydantic_settings import BaseSettings, SettingsConfigDict
from const import ENV_FILE
from loguru import logger


class TortoiseSettings(BaseSettings):
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: str = ""
    POSTGRES_DB: str = ""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) + '.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )
