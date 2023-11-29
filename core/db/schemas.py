from typing import Optional

from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel

from . import *

Tortoise.init_models(['core.db.models'], 'models')

PermissionModel = pydantic_model_creator(
    Permission,
    name='PermissionModel',
    exclude=('app.jobs', 'app.routing_keys'),
)

SettingModel = pydantic_model_creator(
    Setting,
    name='SettingModel',
    exclude=('app.jobs', 'app.routing_keys'),
)

SettingValueModel = pydantic_model_creator(
    SettingValue,
    name='SettingValueModel',
    exclude=('setting.app.jobs', 'setting.app.routing_keys'),
)


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


class GrantedPermissionModel(PydanticModel):
    id: int
    permission: PermissionModel
    user: Optional[UserModelShort]
    team: Optional[TeamModelShort]

    class Config:
        orig_model = GrantedPermission


class UserListModel(PydanticModel):
    id: int
    username: str
    position: Optional[str]
    disabled: bool
    signed_in: bool
    team: Optional[TeamModelShort]
    settings: list[SettingValueModel] = []

    class Config:
        orig_model = User


class UserDetailModel(PydanticModel):
    id: int
    username: str
    position: Optional[str]
    disabled: bool
    signed_in: bool
    team: Optional[TeamModelShort]
    settings: list[SettingValueModel] = []
    # subscriptions: list[RoutingKeySubscriptionModel] = []

    class Config:
        orig_model = User


class TeamListModel(PydanticModel):
    id: int
    name: str
    users: list[UserModelShort] = []

    class Config:
        orig_model = Team


class TeamDetailModel(PydanticModel):
    id: int
    name: str
    users: list[UserModelShort] = []
    settings: list[SettingValueModel] = []
    permissions: list[str] = []

    class Config:
        orig_model = Team