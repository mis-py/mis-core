from typing import Optional
from pydantic import BaseModel

from core.schemas.common import UserModelShort, TeamModelShort
from core.schemas.module import ModuleResponse


class PermissionResponse(BaseModel):
    id: int
    scope: str
    app: ModuleResponse


class GrantedPermissionResponse(BaseModel):
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
