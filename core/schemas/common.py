from tortoise.contrib.pydantic import PydanticModel
from pydantic import BaseModel
from typing import Optional
from core.db.models import Module, User, Team


class UserModelShort(PydanticModel):
    id: int
    username: str
    position: Optional[str]

    class Config:
        orig_model = User


class TeamModelShort(PydanticModel):
    id: int
    name: str

    class Config:
        orig_model = Team


class AppModel(PydanticModel):
    id: int
    name: str
    enabled: bool

    class Config:
        orig_model = Module
