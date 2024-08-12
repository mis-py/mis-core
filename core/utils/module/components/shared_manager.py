from dataclasses import dataclass
from typing import Callable

from core.utils.module.Base.BaseComponent import BaseComponent
from core.utils.module.shared_hub import SharedHub


@dataclass
class SharedTemplate:
    func: Callable
    key: str


class SharedManager(BaseComponent):
    def __init__(self):
        self.shared_funcs: list[SharedTemplate] = []

    def add_shared(self, key: str = None):
        def _wrapper(func):
            func_key = key or func.__name__
            self.shared_funcs.append(SharedTemplate(func=func, key=func_key))
            return func

        return _wrapper

    def extend(self, shared_funcs: list[SharedTemplate]):
        self.shared_funcs.extend(shared_funcs)

    async def pre_init(self, application):
        pass

    async def init(self, app_db_model, is_created: bool):
        for shared_template in self.shared_funcs:
            SharedHub.add_shared_func(
                module_name=self.module.name,
                func=shared_template.func,
                func_key=shared_template.key,
            )

    async def start(self):
        pass

    async def stop(self):
        pass

    async def shutdown(self):
        self.shared_funcs.clear()
