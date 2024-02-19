from pydantic import BaseModel
from fastapi import Body
from datetime import datetime
from typing import Literal, Optional
from core.schemas.common import UserModelShort, TeamModelShort


class JobSchedule(BaseModel):
    interval: int = Body(None, gt=0)
    cron: str | list[str] = Body("", min_length=1)


class JobSchema(BaseModel):
    id: str
    name: str
    status: Literal["running", "paused"]
    next_run_time: Optional[datetime]
    trigger: Optional[dict]
    app: str
    user: UserModelShort
    team: Optional[TeamModelShort]


class JobAdd(BaseModel):
    extra: Optional[dict] = None
    trigger: Optional[JobSchedule] = None


class TaskSchema(BaseModel):
    id: str
    module: str
    name: str
    type: Literal["user", "team"]
    extra_typed: Optional[dict]
    trigger: Optional[dict]
    is_has_jobs: bool
    is_available_add_job: bool
