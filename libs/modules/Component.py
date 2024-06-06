from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .GenericModule import GenericModule


class Component(ABC):
    module: 'GenericModule'

    def bind(self, module: 'GenericModule'):
        self.module = module
        return self

    @abstractmethod
    async def pre_init(self, application):
        """
        Use it for early initialization of module.
        At this stage there is no DB connection.
        Examples: TortoiseModel component must be initialized at this stage
        :application: FastAPI instance
        """

    @abstractmethod
    async def init(self, app_db_model, is_created: bool):
        """
        Runs when a module is installed or every time the module is init
        :app_db_model db instance of module
        :is_created: true when app model created first time
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
