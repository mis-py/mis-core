from typing import Optional

from pydantic import BaseModel
from tortoise.contrib.pydantic import PydanticModel

from core.db.restricted import AccessGroup, RestrictedObject
from core.schemas.common import UserModelShort, AppModel


# Create schema
class CreateAccessGroup(BaseModel):
    name: str
    users_ids: list[int]


# Read schemas
class ReadRestrictedObject(PydanticModel):
    id: int
    object_id: str
    object_app: Optional[AppModel]

    class Config:
        orig_model = RestrictedObject


class ReadAccessGroup(PydanticModel):
    id: int
    name: str
    users: list[UserModelShort]
    # users_ids: list[int]
    allowed_objects: list[ReadRestrictedObject]
    app: Optional[AppModel]

    class Config:
        orig_model = AccessGroup



