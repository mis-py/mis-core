from collections import defaultdict
from typing import Callable

from loguru import logger


class VariableCallbackManager:
    _callbacks: dict[str, dict[str, Callable]] = defaultdict(dict)

    @classmethod
    async def register(cls, module_name: str, variable_key: str, callback: Callable):
        cls._callbacks[module_name][variable_key] = callback

    @classmethod
    async def trigger(cls, module_name: str, variable_key: str, new_value: str):
        if await cls.callback_exists(module_name, variable_key):
            logger.debug(f"Callback triggered for variable '{variable_key}'")
            await cls._callbacks[module_name][variable_key](module_name=module_name, new_value=new_value)

    @classmethod
    async def callback_exists(cls, module_name: str, variable_key: str) -> bool:
        return variable_key in cls._callbacks.get(module_name, {})
