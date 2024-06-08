from dataclasses import dataclass
from typing import Callable, Literal, Coroutine, AsyncGenerator
from functools import wraps
from loguru import logger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from core.db.models import Module
from core.utils.module.generic_module import GenericModule


def job_wrapper(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        obj_to_call = func(*args, **kwargs)

        if isinstance(obj_to_call, Coroutine):
            await obj_to_call
        elif isinstance(obj_to_call, AsyncGenerator):
            async for payload in obj_to_call:
                logger.debug(payload)
                # TODO extend logic here
                # await Eventory.publish(
                #     Message(
                #         body={"dummy_setting": ctx.settings.PRIVATE_SETTING},
                #     ),
                #     routing_keys.DUMMY_EVENT,
                #     ctx.app_name
                # )

    return inner


@dataclass
class TaskTemplate:
    type: Literal['user', 'team']
    func: Callable
    extra_typed: dict
    trigger: IntervalTrigger | CronTrigger | None
    app: Module = None
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