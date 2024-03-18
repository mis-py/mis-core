from tortoise.contrib.pydantic import PydanticModel
from pydantic import BaseModel
from typing import Optional
from core.db.models import Module, User, Team
from services.modules.utils.manifest import ModuleManifest


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
    manifest: Optional[ModuleManifest] = None

    class Config:
        orig_model = Module
