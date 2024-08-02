import time
from dataclasses import dataclass
from typing import Callable, Literal, Coroutine, AsyncGenerator
from functools import wraps
from pydoc import locate
from loguru import logger
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from pydantic import create_model, ValidationError

from core.db.models import Module
from core.exceptions import ValidationFailed
from core.services.jobs_storage import JobExecutionStorage
from core.utils.app_context import AppContext


def get_trigger(input_trigger: int | str | list[str]):
    if isinstance(input_trigger, int):
        return IntervalTrigger(seconds=input_trigger)
    elif isinstance(input_trigger, str):
        return CronTrigger.from_crontab(input_trigger)
    elif isinstance(input_trigger, list) and len(input_trigger) > 0:
        return OrTrigger([CronTrigger.from_crontab(c) for c in input_trigger])
    else:
        return None


def validate_trigger_from_request(trigger, task_trigger):
    # trigger logic:
    # if specified in request - use trigger in request
    # else use trigger defined by task

    # requested trigger serialized in DB as is
    # task trigger not saved in DB and constructing every time from task, so in DB in will be {"data": None}

    # construct trigger from request
    out_trigger = get_trigger(trigger)

    # if trigger not set in request then use task trigger
    if not out_trigger and task_trigger:
        out_trigger = task_trigger

    # if task trigger also None - raise an exception
    # todo in future None trigger can be valid for task pre-creation. then edit task to apply trigger
    if out_trigger is None:
        raise ValidationFailed(f"Argument 'trigger' required for this task!")

    return out_trigger


def validate_extra_params_from_request(extra, task_extra):
    fields = {
        extra_name: (
            locate(extra_type),
            ...
        ) for extra_name, extra_type in task_extra.items()
    }

    ValidateExtraParams = create_model(
        'ValidateExtraParams',
        **fields
    )

    try:
        # validate received extra params and convert to appropriate types
        validated = ValidateExtraParams.model_validate(extra)
        return validated.model_dump()

    except ValidationError:
        # logger.warning([e['msg'] for e in ex.json()])
        raise ValidationFailed("Requested extra params has incorrect values")


def job_wrapper(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        obj_to_call = func(*args, **kwargs)

        job_meta = kwargs.get('job_meta')
        job_id = job_meta.job_id
        with logger.contextualize(filter_name=f"{job_meta.task_name}-{job_meta.job_id}", context_key=f"JOB:{job_meta.task_name}:{job_meta.job_id}"):
            logger.debug("Job started!")
            JobExecutionStorage.insert(job_id)

            start_time = time.time()
            try:
                if isinstance(obj_to_call, Coroutine):
                    return_info = await obj_to_call
                    logger.debug(return_info)
                    JobExecutionStorage.set_return(job_id, value=return_info)
                elif isinstance(obj_to_call, AsyncGenerator):
                    async for payload in obj_to_call:
                        logger.debug(payload)
                        JobExecutionStorage.insert_yield(job_id, value=payload)
                JobExecutionStorage.set_end(job_id)
            except Exception as e:
                JobExecutionStorage.set_exception(job_id, value=e)
                logger.exception(e)
            finally:
                execution_seconds = round(time.time() - start_time, 6)
                JobExecutionStorage.set_time_execution(job_id, seconds=execution_seconds)
                logger.debug(f"Job finished! {execution_seconds} seconds elapsed")

    return inner


@dataclass
class TaskTemplate:
    type: Literal['user', 'team']
    func: Callable
    extra_typed: dict
    trigger: IntervalTrigger | CronTrigger | OrTrigger | None
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


@dataclass
class JobMeta:
    job_id: int
    job_name: str
    trigger: IntervalTrigger | CronTrigger | OrTrigger
    task_name: str
    user_id: int
    module_id: int


def format_trigger(trigger: IntervalTrigger | CronTrigger | OrTrigger | None):
    match trigger:
        case IntervalTrigger():
            return trigger.interval.seconds
        case CronTrigger():
            return make_string_cron(trigger)
        case OrTrigger():
            return [make_string_cron(cron_trigger) for cron_trigger in trigger.triggers]
        case _:
            return None


def make_string_cron(trigger: CronTrigger):
    minute_index = trigger.FIELD_NAMES.index('minute')
    hour_index = trigger.FIELD_NAMES.index('hour')
    day_index = trigger.FIELD_NAMES.index('day')
    month_index = trigger.FIELD_NAMES.index('month')
    day_of_week_index = trigger.FIELD_NAMES.index('day_of_week')

    minute = str(trigger.fields[minute_index])
    hour = str(trigger.fields[hour_index])
    day = str(trigger.fields[day_index])
    month = str(trigger.fields[month_index])
    day_of_week = str(trigger.fields[day_of_week_index])

    return f"{minute} {hour} {day} {month} {day_of_week}"
