from pydantic import BaseModel
from typing import Optional
from core.schemas.common import UserModelShort
from core.schemas.variable import VariableValueResponse
from core.utils.schema import MisModel


class TeamCreate(BaseModel):
    name: str
    permissions: Optional[list[str]] = []
    users_ids: Optional[list[int]] = []
    variables: Optional[list[VariableValueResponse]] = []


class TeamUpdate(BaseModel):
    name: str
    permissions: Optional[list[str]] = []
    users_ids: Optional[list[int]] = []
    variables: Optional[list[VariableValueResponse]] = []


class TeamResponse(BaseModel):
    id: int
    name: str
    users: list[UserModelShort] = []
    variables: list[VariableValueResponse] = []
    permissions: list[str] = []


class TeamListResponse(BaseModel):
    id: int
    name: str
    users: list[UserModelShort] = []
