from pydantic import BaseModel, Field
from core.routes.variable import UpdateVariableModel
from tortoise.contrib.pydantic import PydanticModel
from pydantic import BaseModel
from typing import Optional
from core.db.models import User
from core.schemas.common import TeamModelShort
from core.schemas.variable import VariableValueModel


class UserDetailModel(PydanticModel):
    id: int
    username: str
    position: Optional[str]
    disabled: bool
    signed_in: bool
    team: Optional[TeamModelShort]
    variables: list[VariableValueModel] = []
    # subscriptions: list[RoutingKeySubscriptionModel] = []

    class Config:
        orig_model = User


class UserListModel(PydanticModel):
    id: int
    username: str
    position: Optional[str]
    disabled: bool
    signed_in: bool
    team: Optional[TeamModelShort]
    variables: list[VariableValueModel] = []

    class Config:
        orig_model = User


class EditUserInput(BaseModel):
    username: Optional[str] = Field(max_length=20, min_length=3)
    team_id: int = None
    new_password: str = ''
    disabled: bool = None
    position: Optional[str] = Field(max_length=100)


class EditUserMe(BaseModel):
    username: Optional[str] = Field(max_length=20, min_length=3)


class CreateUserInput(BaseModel):
    username: str = Field(max_length=20, min_length=3)
    password: str
    team_id: int = None
    settings: Optional[list[UpdateVariableModel]] = []
    position: Optional[str] = Field(max_length=100)
    permissions: Optional[list[str]] = []