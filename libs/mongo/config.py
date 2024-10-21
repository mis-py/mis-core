from pydantic_settings import BaseSettings


class MongoSettings(BaseSettings):
    MONGO_INITDB_ROOT_USERNAME: str = "root"
    MONGO_INITDB_ROOT_PASSWORD: str = "root"
    MONGO_INITDB_DATABASE: str = "mis"
    MONGO_HOST: str = "mis-mongo"
    MONGO_PORT: str = "27017"
