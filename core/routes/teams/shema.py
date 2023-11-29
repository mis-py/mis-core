from typing import Optional
from pydantic import BaseModel
from core.routes.variables.settings import UpdateSettingModel


class TeamData(BaseModel):
    name: str | None
    permissions: list[str] | None
    users_ids: list[int] | None
    settings: Optional[list[UpdateSettingModel]] = []