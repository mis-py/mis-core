from typing import Optional

from pydantic import BaseModel
from tortoise.contrib.pydantic import PydanticModel

from core.db import UserGroup
from core.db.schemas import UserModelShort
from core.routes.schema import AppModel


class UserIds(BaseModel):
    users_ids: list[int]


# Create schema
class CreateAccessGroup(BaseModel):
    name: str
    users_ids: Optional[UserIds]


# Read schema
class ReadAccessGroup(PydanticModel):
    id: int
    name: str
    # users: list[UserModelShort]
    users_ids: UserIds
    # allowed_objects: list[RestrictedObjectModel]
    # app: Optional[AppModel]

    class Config:
        orig_model = UserGroup
