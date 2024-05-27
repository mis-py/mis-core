from datetime import datetime

from tortoise.contrib.pydantic import PydanticModel

from core.schemas.common import UserModelShort


class ReplacementHistoryBaseModel(PydanticModel):
    id: int
    replaced_by: UserModelShort
    date_changed: datetime
    reason: str


class TrackerInstanceBaseModel(PydanticModel):
    id: int
    name: str
    description: str
