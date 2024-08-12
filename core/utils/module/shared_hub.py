from collections import defaultdict
from typing import Callable


class SharedHub:
    """
    Implemented to avoid import dependencies between modules
    Store and execute shared modules logic
    """

    _shared_funcs = defaultdict(dict)

    @classmethod
    def add_shared_func(cls, module_name: str, func: Callable, func_key: str) -> None:
        cls._shared_funcs[module_name][func_key] = func

    @classmethod
    async def execute(cls, module: str, func_key: str, *args, **kwargs):
        module_funcs = cls._shared_funcs.get(module)
        if not module_funcs:
            raise ValueError(f"No shared funcs for module '{module}'")

        execute_func = module_funcs.get(func_key)
        if not execute_func:
            raise ValueError(f"Not found shared func '{func_key}'")

        return await execute_func(*args, **kwargs)
