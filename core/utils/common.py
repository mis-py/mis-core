import functools
import inspect
import os
import datetime
import random
import re
import string

import loguru
import pytz
from fastapi.routing import APIRoute
from pydantic import BaseModel
from const import LOGS_DIR, TIMEZONE
from config import CoreSettings
from core.exceptions import MISError

settings = CoreSettings()


def generate_unique_id(route: APIRoute):
    try:
        return f"{route.tags[0]}-{route.name}"
    except:
        return route.name


def convert_appropriate(value: str, type_cls: type[str] | type[int] | type[bool] | type[float] | type[list] | type[tuple]):
    loguru.logger.debug(f'GOT {repr(value)} -> {type_cls}')
    match type_cls.__name__:
        case 'str':
            return value
        case 'int':
            if value.isdigit():
                return int(value)
        case 'bool':
            if value == 'True':
                return True
            elif value == 'False':
                return False
        case 'float':
            if value.replace('.', '').isdigit():
                return float(value)
        case 'list' | 'tuple':
            values = value.split(',')
            return type_cls(map(str.strip, values))
    raise TypeError(f"Can't use value '{value}' for '{type_cls.__name__}' type")


def async_partial(coro, *partial_args, **partial_kwargs):
    @functools.wraps(coro)
    async def _function(*args, **kwargs):
        return await coro(*partial_args, *args, **partial_kwargs, **kwargs)
    return _function


def get_log_levels_above(level):
    log_levels = loguru.logger._core.levels
    level_value = log_levels[level].no
    return [name for name, level_obj in log_levels.items() if level_obj.no >= level_value]


def create_new_logger(directory: str, logger_id: str):
    new_logger = loguru.logger.bind(logger_id=logger_id)
    loguru.logger.add(
        LOGS_DIR / f"{directory}/{logger_id}/{logger_id}.log",
        format=settings.LOGGER_FORMAT,
        filter=lambda record: record["extra"].get("logger_id") == logger_id,
        rotation=settings.LOG_ROTATION,
        serialize=True,
    )
    new_logger = new_logger.opt(ansi=True)
    return new_logger


def find_log_file(name: str, log_dir: os.path, date: datetime.date = None) -> str | None:
    for filename in os.listdir(log_dir):
        if not date and filename == name + '.log':  # current log file
            return filename
        if date and f"{name}.{date}" in filename:  # rotated log file with date in name
            return filename
    return None


def select_logs_by_hour(file_path: os.path, hour: int) -> str:
    with open(file_path, 'r') as log_file:
        lines = log_file.readlines()
    formatted_hour = f'{hour:02d}'
    selected_lines = [line for line in lines if line[11:13] == formatted_hour]
    return ''.join(selected_lines)


def get_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


def signature_to_dict(func) -> dict[str, str]:
    """Get func params with typing"""
    func_signature = inspect.signature(func)
    parameters = func_signature.parameters
    return {key: value.annotation.__name__ for key, value in parameters.items()}


def validate_task_extra(extra: dict, kwargs_typing: dict):
    if extra and extra.keys() != kwargs_typing.keys():
        raise MISError(f"Task key arguments not valid")

    kwargs = {}
    for key, value in kwargs_typing.items():
        type_instance = globals()["__builtins__"][value]
        try:
            kwargs[key] = type_instance(extra[key])
        except ValueError:
            raise MISError(f"Type of arguments not valid")
    return kwargs


def pydatic_model_to_dict(model: BaseModel) -> dict[str, dict[str, str]]:
    result = {}
    for name, field in model.model_fields.items():
        result[name] = {
            "type": field.annotation.__name__,
            "required": field.is_required,
        }
    return result


def custom_log_timezone(record):
    tz = pytz.timezone(TIMEZONE)
    dt = datetime.datetime.now(tz)
    record["extra"]["datetime"] = dt.strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]


def camel_to_spaces(camel_string: str):
    list_words = re.split(r'(?=[A-Z])', camel_string)
    return ' '.join(list_words).strip()


def exclude_none_values(data: dict):
    return {key: value for key, value in data.items() if value is not None}
