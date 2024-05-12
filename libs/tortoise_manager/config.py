from pydantic_settings import BaseSettings, SettingsConfigDict
from const import ENV_FILE


class TortoiseSettings(BaseSettings):
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: str = ""
    POSTGRES_DB: str = ""

    POSTGRES_CREATE_DB: bool = False

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) + '.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )
