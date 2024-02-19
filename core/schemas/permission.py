from typing import Optional
from pydantic import BaseModel
from core.db.models import Permission, GrantedPermission
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel
from core.schemas.common import UserModelShort, TeamModelShort


PermissionModel = pydantic_model_creator(
    Permission,
    name='PermissionModel',
    exclude=('app.jobs', 'app.routing_keys', 'granted_permissions'),
)


class GrantedPermissionModel(PydanticModel):
    id: int
    permission: PermissionModel
    user: Optional[UserModelShort]
    team: Optional[TeamModelShort]

    class Config:
        orig_model = GrantedPermission


class ReadPermission(BaseModel):
    permission_id: int
    name: str
    scope: str
    app_id: int


class UpdatePermissionModel(BaseModel):
    permission_id: int
    granted: bool | None = None
