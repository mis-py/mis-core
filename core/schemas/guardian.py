from typing import Optional

from pydantic import BaseModel

from core.schemas.common import AppModel


class CreateAccessGroup(BaseModel):
    name: str
    users_ids: list[int]


class UpdateAccessGroup(BaseModel):
    name: Optional[str] = None
    users_ids: Optional[list[int]] = None


class ReadAccessGroup(BaseModel):
    id: int
    name: str


############################################
class ReadContentType(BaseModel):
    id: int
    module: AppModel
    model: str


############################################
class ReadPermission(BaseModel):
    id: int
    code_name: str
    name: str


############################################
class ReadUserPerm(BaseModel):
    id: int
    object_pk: str
    content_type: ReadContentType
    permission: ReadPermission
    user_id: int


class SimpleUserPerm(BaseModel):
    id: int
    object_pk: str
    content_type_id: int
    permission_id: int
    user_id: int


class CreateUserPerm(BaseModel):
    object_pk: str
    content_type_id: int
    permission_id: int
    user_id: int


############################################
class ReadGroupPerm(BaseModel):
    id: int
    object_pk: str
    content_type: ReadContentType
    permission: ReadPermission
    group_id: int


class SimpleGroupPerm(BaseModel):
    id: int
    object_pk: str
    content_type_id: int
    permission_id: int
    group_id: int


class CreateGroupPerm(BaseModel):
    object_pk: str
    content_type_id: int
    permission_id: int
    group_id: int
