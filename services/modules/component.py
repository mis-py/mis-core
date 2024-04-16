from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.modules.utils import BaseModule


class Component(ABC):
    module: 'BaseModule'

    def bind(self, module: 'BaseModule'):
        self.module = module
        return self

    @abstractmethod
    async def pre_init(self):
        """
        Use it for early initialization of module.
        At this stage there is no DB connection.
        Examples: TortoiseModel component must be initialized at this stage
        """

    @abstractmethod
    async def init(self, application, app_db_model, is_created: bool):
        """
        Runs when a module is installed or every time the module is init
        :is_created: true when app model created first time
        :application: FastAPI instance
        """

    @abstractmethod
    async def start(self):
        """Runs after "start" every time the module is started (if enabled)"""

    @abstractmethod
    async def stop(self):
        """Runs when module stopped"""

    @abstractmethod
    async def shutdown(self):
        """Runs when module shutdown"""
