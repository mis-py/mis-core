from typing import Optional
from pydantic import BaseModel
from tortoise.contrib.pydantic import PydanticModel

from core.schemas.common import UserModelShort, TeamModelShort
from core.schemas.module import ModuleShortResponse


class PermissionResponse(PydanticModel):
    id: int
    scope: str
    app: ModuleShortResponse


class GrantedPermissionResponse(PydanticModel):
    id: int
    permission: PermissionResponse
    user: Optional[UserModelShort]
    team: Optional[TeamModelShort]


class UserPermDetailResponse(BaseModel):
    permission_id: int
    name: str
    scope: str
    app_id: int


class PermissionUpdate(BaseModel):
    permission_id: int
    granted: bool | None = None
