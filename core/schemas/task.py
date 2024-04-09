from pydantic import BaseModel
from fastapi import Body
from typing import Literal, Optional
from core.utils.schema import MisModel
from core.db.models import ScheduledJob


class JobScheduleUpdate(BaseModel):
    interval: int = Body(None, gt=0)
    cron: str | list[str] = Body("", min_length=1)


class JobResponse(MisModel):
    id: int
    name: str
    status: ScheduledJob.StatusTask
    app_id: Optional[int]
    user_id: Optional[int]
    team_id: Optional[int]


class JobCreate(BaseModel):
    task_id: str
    extra: Optional[dict] = None
    trigger: Optional[JobScheduleUpdate] = None
    type: Literal["user", "team"]


class TaskResponse(BaseModel):
    id: str
    # module: str
    name: str
    type: Literal["user", "team"]
    extra_typed: Optional[dict]
    trigger: Optional[dict]
    is_has_jobs: bool
    is_available_add_job: bool
