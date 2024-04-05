from core.routes.variable import UpdateVariableModel
from pydantic import BaseModel
from typing import Optional
from core.schemas.common import UserModelShort
from core.schemas.variable import VariableValueModel
from core.utils.schema import MisModel


class TeamCreate(BaseModel):
    name: str
    permissions: Optional[list[str]] = []
    users_ids: Optional[list[int]] = []
    variables: Optional[list[UpdateVariableModel]] = []


class TeamUpdate(BaseModel):
    name: str
    permissions: Optional[list[str]] = []
    users_ids: Optional[list[int]] = []
    variables: Optional[list[UpdateVariableModel]] = []


class TeamResponse(MisModel):
    id: int
    name: str
    users: list[UserModelShort] = []
    variables: list[VariableValueModel] = []
    permissions: list[str] = []


class TeamListResponse(BaseModel):
    id: int
    name: str
    users: list[UserModelShort] = []
