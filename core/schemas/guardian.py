from typing import Optional

from pydantic import BaseModel

from core.schemas.common import AppModel
from core.utils.schema import MisModel


class AccessGroupCreate(BaseModel):
    name: str
    users_ids: Optional[list[int]] = []


class AccessGroupUpdate(BaseModel):
    name: Optional[str] = None


class AccessGroupResponse(MisModel):
    id: int
    name: str


class ContentTypeResponse(BaseModel):
    id: int
    module: AppModel
    model: str


class PermissionResponse(BaseModel):
    id: int
    code_name: str
    name: str


class ObjectPermBase(MisModel):
    """
    Model with base fields for user ang group permission
    """
    object_pk: str
    content_type_id: int
    permission_id: int


class UserPermResponse(ObjectPermBase):
    id: int
    user_id: int


class GroupPermResponse(ObjectPermBase):
    id: int
    group_id: int


class UserPermCreate(ObjectPermBase):
    user_id: int


class GroupPermCreate(ObjectPermBase):
    group_id: int


class ObjectPermDetailBase(BaseModel):
    """
    Model with base fields for user ang group permission
    with nested models
    """

    id: int
    object_pk: str
    content_type: ContentTypeResponse
    permission: PermissionResponse


class UserPermDetailResponse(ObjectPermDetailBase):
    user_id: int


class GroupPermDetailResponse(ObjectPermDetailBase):
    group_id: int
