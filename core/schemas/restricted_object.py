from typing import Optional

from tortoise.contrib.pydantic import PydanticModel

from core.db.restricted import RestrictedObject
from core.schemas.common import AppModel


class RestrictedObjectModel(PydanticModel):
    id: int
    object_id: str
    object_app: Optional[AppModel]

    class Config:
        orig_model = RestrictedObject
