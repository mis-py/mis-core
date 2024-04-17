import dataclasses
from typing import Callable


@dataclasses.dataclass
class BaseModule:
    """
    Basic module data container
    """
    # System name of module
    name: str = None
    # Verbose name of module
    display_name: str = None
    # Description of module
    description: str = None
    # Module version
    version: str = None
    # Module author
    author: str = None
    # Module category
    category: str = None
    # Permissions that module is required to use
    permissions: dict = dataclasses.field(default_factory=dict)

    pre_init_event: Callable = None
    init_event: Callable = None
    shutdown_event: Callable = None
    start_event: Callable = None
    stop_event: Callable = None

    @property
    def info(self):
        # return dataclasses.asdict({x: self.__dict__[x] for x in self.__dict__ if x != 'model'})
        return {
            "name": self.name,
            'display_name': self.display_name,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'category': self.category,
        }

    async def pre_init(self):
        if self.pre_init_event:
            await self.pre_init_event(self)

    async def init(self):
        if self.init_event:
            await self.init_event(self)

    async def shutdown(self):
        if self.shutdown_event:
            await self.shutdown_event(self)

    async def start(self):
        if self.start_event:
            await self.start_event(self)

    async def stop(self):
        if self.stop_event:
            await self.stop_event(self)

