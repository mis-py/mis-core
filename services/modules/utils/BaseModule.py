
from typing import Callable
from core.db.models import Module
from core.exceptions import MISError
from services.modules.component import Component
from services.modules.utils.manifest import ModuleDependency
from loguru import logger


class BaseModule:
    """
    Basic module data container
    """
    # System name of module
    name: str
    # Verbose name of module
    display_name: str
    # Description of module
    description: str
    # Module version
    version: str
    # Module author
    author: str
    # Module category
    category: str
    # Permissions that module is required to use
    permissions: dict

    # List of module components
    pre_init_components: list[Component]
    components: list[Component]

    # Other modules as dependencies
    dependencies: list[ModuleDependency]

    # If auth disabled routes will not have access to current user
    auth_disabled: bool

    # DB reference to app model
    _model: Module

    # will be True on very first model init
    _is_created: bool

    pre_init_event: Callable
    init_event: Callable
    shutdown_event: Callable
    start_event: Callable
    stop_event: Callable

    def __init__(
            self,
            pre_init_event: Callable = None,
            init_event: Callable = None,
            shutdown_event: Callable = None,
            start_event: Callable = None,
            stop_event: Callable = None,
            pre_init_components: list[Component] = None,
            components: list[Component] = None
    ):
        self.pre_init_event = pre_init_event
        self.init_event = init_event
        self.shutdown_event = shutdown_event
        self.start_event = start_event
        self.stop_event = stop_event
        self.pre_init_components = pre_init_components
        self.components = components

    async def _set_state(self, state: Module.AppState) -> None:
        self._model.state = state
        await self._model.save()

    def get_state(self) -> Module.AppState:
        return self._model.state

    def get_id(self) -> int:
        return self._model.pk

    def is_enabled(self) -> bool:
        return self._model.enabled

    async def pre_init(self) -> bool:
        """
        pre_init calls automatically on system startup
        """
        try:
            for component in self.pre_init_components:
                await component.bind(self).pre_init()
                logger.debug(f'[{self.name}] component {component.__class__.__name__} pre_init finished')

            # if all components pre_init success
            if self.pre_init_event:
                await self.pre_init_event(self)

            return True

        except Exception as error:
            logger.exception(error)
            logger.error(f"[{self.name}] Component and module pre_init failed. {error.__class__.__name__}")

        return False

    async def bind_model(self, model, is_created) -> bool:
        self._model = model
        self._is_created = is_created

        for component in self.components:
            component.bind(self)

        return True

    async def init(self, application, from_system=False) -> bool:
        if not from_system and self._model.state not in [Module.AppState.SHUTDOWN, Module.AppState.PRE_INITIALIZED, Module.AppState.ERROR]:
            raise MISError("Can not init module that is not in 'SHUTDOWN' or 'PRE_INITIALIZED' or 'ERROR' state")

        try:
            for component in self.components:
                await component.init(application, self._model, self._is_created)
                logger.debug(f'[{self.name}] component {component.__class__.__name__} init finished')

            # if all components init success
            if self.init_event:
                await self.init_event(self)

            # not change state if it is system call
            if not from_system:
                await self._set_state(Module.AppState.INITIALIZED)

            return True

        except Exception as error:
            logger.exception(error)
            logger.error(f"[{self.name}] Component and module init failed. {error.__class__.__name__}")

            await self._set_state(Module.AppState.ERROR)

        return False

    async def start(self, from_system=False) -> bool:
        if self._model.state == Module.AppState.ERROR:
            raise MISError("Can not start module that is in 'ERROR' state")
        if not from_system and self._model.state not in [Module.AppState.STOPPED, Module.AppState.INITIALIZED]:
            raise MISError("Can not start module that not in 'STOPPED' or 'INITIALIZED' state ")

        try:
            for component in self.components:
                await component.start()
                logger.debug(f'[{self.name}] component {component.__class__.__name__} started')

            # if all components start success
            if self.start_event:
                await self.start_event(self)

            # not change state if it is system call
            if not from_system:
                await self._set_state(Module.AppState.RUNNING)

            return True

        except Exception as error:
            logger.exception(error)
            logger.error(f"[{self.name}] Component and module start failed. {error.__class__.__name__}")

            await self._set_state(Module.AppState.ERROR)

        return False

    async def stop(self, from_system=False) -> bool:
        if self._model.state == Module.AppState.ERROR:
            raise MISError("Can not stop module that is in 'ERROR' state")
        if not from_system and self._model.state != Module.AppState.RUNNING:
            raise MISError("Can not stop module that not in 'RUNNING' state ")

        for component in self.components:
            await component.stop()
            logger.debug(f'[{self.name}] component {component.__class__.__name__} stopped')

        if self.stop_event:
            await self.stop_event(self)

        # not change state if it is system call
        if not from_system:
            await self._set_state(Module.AppState.STOPPED)

        return True

    async def shutdown(self, from_system=False) -> bool:
        if self._model.state == Module.AppState.ERROR:
            raise MISError("Can not shutdown module that is in 'ERROR' state")
        if not from_system and self._model.state not in [Module.AppState.STOPPED, Module.AppState.INITIALIZED, Module.AppState.PRE_INITIALIZED]:
            raise MISError("Can not shutdown module that not in 'STOPPED', 'INITIALIZED', 'PRE_INITIALIZED' state")

        for component in self.components:
            await component.shutdown()
            logger.debug(f'[{self.name}] component {component.__class__.__name__} shutdown finished')

        if self.shutdown_event:
            await self.shutdown_event(self)

        # not change state if it is system call
        if not from_system:
            await self._set_state(Module.AppState.SHUTDOWN)

        return True


