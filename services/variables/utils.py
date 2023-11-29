from loguru import logger
from tortoise.exceptions import MultipleObjectsReturned

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.db import User


def type_convert(value: str, to_type: str):
    type_convertors = {
        "text": str,
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
    }
    return type_convertors[to_type](value)


async def get_user_by_setting(key: str, value):
    try:
        return await User.get_or_none(
            settings__value=value,
            settings__setting__key=key
        )
    except MultipleObjectsReturned:
        logger.error(f"{key} value duplicated in users")
        return None
