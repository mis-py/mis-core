from pydantic_settings import BaseSettings, SettingsConfigDict
from const import ENV_FILE


class MongoSettings(BaseSettings):
    MONGODB_URI: str = "mongodb://root:root@mongo:27017/"
    MONGODB_TABLE: str = "mis"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) + '.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )
