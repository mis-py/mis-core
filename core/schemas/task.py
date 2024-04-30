from pydantic import BaseModel, field_validator
import re
from typing import Literal, Optional
from core.utils.schema import MisModel
from core.db.models import ScheduledJob


class JobTrigger(MisModel):
    trigger: Optional[int | str | list[str]] = None

    # TODO make it work
    # @field_validator('trigger')
    # @classmethod
    # def check_trigger(cls, value: int | str | list[str]):
    #     regexp = r"/^(\*|((\*\/)?[1-5]?[0-9])) (\*|((\*\/)?[1-5]?[0-9])) (\*|((\*\/)?(1?[0-9]|2[0-3]))) (\*|((\*\/)?([1-9]|[12][0-9]|3[0-1]))) (\*|((\*\/)?([1-9]|1[0-2]))) (\*|((\*\/)?[0-6]))$/"
    #     if isinstance(value, int) and value <= 60:
    #         raise ValueError("Int value must be greater or equal 60")
    #     if isinstance(value, str) and not re.match(regexp, value):
    #         raise ValueError(f"Wrong cron expression '{value}'")
    #     if isinstance(value, list):
    #         for i, string_item in enumerate(value):
    #             if isinstance(string_item, str) and not re.match(regexp, string_item):
    #                 raise ValueError(f"Wrong cron expression '{string_item}' at position {i} of list.")
    #
    #     return value


# class SchedulerJob(MisModel):
#     id: str
#     name: str
#     func: str
#     # args: tuple|list
#     # kwargs:dict
#     # coalesce:bool
#     trigger: str
#     next_run_time: str


class JobResponse(JobTrigger):
    job_id: int
    name: str
    status: ScheduledJob.StatusTask
    app_id: Optional[int]
    user_id: Optional[int]
    team_id: Optional[int]


class JobCreate(JobTrigger):
    task_name: str
    extra: Optional[dict] = None
    type: Literal["user", "team"]


class TaskResponse(JobTrigger):
    id: str
    name: str
    type: Literal["user", "team"]
    extra_typed: Optional[dict]

    #is_has_jobs: bool
    #is_available_add_job: bool
