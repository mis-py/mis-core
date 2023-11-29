from tortoise.contrib.pydantic import PydanticModel
from pydantic import BaseModel

from core.db import App


class AppModel(PydanticModel):
    id: int
    name: str
    enabled: bool

    class Config:
        orig_model = App
