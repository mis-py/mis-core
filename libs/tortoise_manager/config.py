from pydantic_settings import BaseSettings
from const import ENV_FILE


class TortoiseSettings(BaseSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "mis-postgres"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "mis"

    POSTGRES_CREATE_DB: bool = False
