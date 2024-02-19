from core.routes.variable import UpdateVariableModel
from tortoise.contrib.pydantic import PydanticModel
from pydantic import BaseModel
from typing import Optional
from core.db.models import Team
from core.schemas.common import UserModelShort
from core.schemas.variable import VariableValueModel


class TeamDetailModel(PydanticModel):
    id: int
    name: str
    users: list[UserModelShort] = []
    variables: list[VariableValueModel] = []
    permissions: list[str] = []

    class Config:
        orig_model = Team


class TeamListModel(PydanticModel):
    id: int
    name: str
    users: list[UserModelShort] = []

    class Config:
        orig_model = Team


class TeamData(BaseModel):
    name: str | None
    permissions: list[str] | None
    users_ids: list[int] | None
    variables: Optional[list[UpdateVariableModel]] = []