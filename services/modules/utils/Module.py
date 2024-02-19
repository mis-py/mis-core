from abc import abstractmethod

# from dataclasses import dataclass
# from typing import Callable, Literal, Optional

# from apscheduler.job import Job
import dataclasses
from typing import Callable

from pydantic_settings import BaseSettings
from core.db.models import Module

# from libs.eventory import Consumer
from .BaseModule import BaseModule
from services.modules.component import Component

from .module_dependency import ModuleDependency
from services.modules.context import AppContext
from services.variables.variables import VariablesManager


@dataclasses.dataclass
class ModuleTemplate(BaseModule):
    # DB reference to app model
    model: Module = None
    # List of module components
    pre_init_components: list[Component] = dataclasses.field(default_factory=list[Component])
    components: list[Component] = dataclasses.field(default_factory=list[Component])

    app_settings: BaseSettings = None
    user_settings: BaseSettings = None

    # Other modules as dependencies
    dependencies: list[ModuleDependency] = None

    initialized: bool = False
    started: bool = False

    # If auth disabled routes will not have access to current user
    auth_disabled: bool = False

    # def __init__(
    #     self,
    #     components: list[Component],
    #     model: App,
    #     permissions: dict = None,
    #     app_settings: BaseSettings = None,
    #     user_settings: BaseSettings = None,
        # notification_sender: Callable = None,
    # ):
        # self.permissions = permissions or {}
        # self.app_settings = app_settings or {}
        # self.user_settings = user_settings or {}
        # self.sender: Optional[Callable] = notification_sender

        # self.module_proxy = ModuleProxy(self, misapp.eventory, misapp.redis, app_settings, user_settings)

        # self.jobs: list[Job] = []
        # self.consumers: list[Consumer] = []

        # self.model: App = model
        # self.components: list[Component] = components

    # if user or team is defined then they will be available in context
    async def get_context(self, user=None, team=None):
        return AppContext(
            module=self,
            settings=await VariablesManager.make_variable_set(user=user, team=team, app=self.model)
        )


