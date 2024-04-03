from pydantic import BaseModel, Field
from core.routes.variable import UpdateVariableModel
from typing import Optional
from core.schemas.common import TeamModelShort
from core.schemas.variable import VariableValueModel
from core.utils.schema import MisModel


class UserCreate(BaseModel):
    username: str
    password: str
    team_id: int = None
    position: Optional[str] = Field(max_length=100)
    permissions: Optional[list[str]] = []
    variables: Optional[list[UpdateVariableModel]] = []


class UserUpdate(BaseModel):
    username: Optional[str] = Field(max_length=20, min_length=3)
    team_id: int = None
    new_password: str = ''
    disabled: bool = None
    position: Optional[str] = Field(max_length=100)


class UserSelfUpdate(BaseModel):
    username: str = Field(max_length=20, min_length=3)


class UserResponse(MisModel):
    id: int
    username: str = Field(max_length=20, min_length=3)
    position: Optional[str]
    disabled: bool
    signed_in: bool
    team: Optional[TeamModelShort]
    settings: list[VariableValueModel] = []


class UserListResponse(BaseModel):
    id: int
    username: str
    position: Optional[str]
    disabled: bool
    signed_in: bool
    team: Optional[TeamModelShort]
    settings: list[VariableValueModel] = []
