from dataclasses import dataclass
from typing import Callable, Literal

# from .exceptions import SchedulerException
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from services.modules.utils import BaseModule


@dataclass
class Task:
    type: Literal['user', 'team']
    func: Callable
    extra_typed: dict
    trigger: IntervalTrigger | CronTrigger | None
    # module: BaseModule | None
    autostart: bool

    @property
    def name(self):
        return self.func.__name__

    def make_id(self, app_name: str, obj_id: int, extra: dict):
        job_id = f"{self.type}_{obj_id}:{app_name}:{self.name}"
        if extra:
            unique_suffix = ":".join(f"{key}={value}" for key, value in extra.items())
            return f"{job_id}:{unique_suffix}"
        return job_id
