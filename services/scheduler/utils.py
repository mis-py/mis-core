from dataclasses import dataclass
from typing import Callable, Literal

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from services.modules.utils import GenericModule


@dataclass
class Task:
    type: Literal['user', 'team']
    func: Callable
    extra_typed: dict
    trigger: IntervalTrigger | CronTrigger | None
    # module: BaseModule = None
    module: GenericModule = None
    autostart: bool = False
    single_instance: bool = False

    @property
    def name(self):
        return self.func.__name__

    # def make_id(self, obj_id: int, extra: dict):
    #     job_id = f"{obj_id}:{self.type}:{self.module.name}:{self.name}"
    #     if extra:
    #         unique_suffix = ":".join(f"{key}={value}" for key, value in extra.items())
    #         return f"{job_id}:{unique_suffix}"
    #     return job_id
