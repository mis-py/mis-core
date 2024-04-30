from pydantic import BaseModel, Field
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
    name: Optional[str] = Field(None, max_length=20, min_length=3)
    permissions: Optional[list[str]] = []
    users_ids: Optional[list[int]] = []
    variables: Optional[list[VariableValueResponse]] = []


class TeamResponse(MisModel):
    id: int
    name: str
    users: list[UserModelShort] = []
    variables: list[VariableValueResponse] = []
    permissions: list[str] = []


class TeamListResponse(BaseModel):
    id: int
    name: str
    users: list[UserModelShort] = []
