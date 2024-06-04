from loguru import logger

from core.db.dataclass import AppState
from core.dependencies.services import get_variable_value_service
from core.exceptions import MISError

from libs.eventory import Eventory

from .utils.BaseModule import BaseModule
from .AppContext import AppContext

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .utils.ModuleManifest import ModuleManifest


class GenericModule(BaseModule):
    # TODO does it really need here??? move it to manifest?
    # app_settings: BaseSettings = None
    # user_settings: BaseSettings = None

    # def __init__(
    #     self,
    #     components: list[Component],
    #     model: App,
    #     permissions: dict = None,
    #     app_settings: BaseSettings = None,
    #     user_settings: BaseSettings = None,
    # notification_sender: Callable = None,
    # ):
    # self.sender: Optional[Callable] = notification_sender

    async def _set_state(self, state: AppState) -> None:
        self._model.state = state
        await self._model.save()

    def get_state(self) -> AppState:
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
        if not from_system and self._model.state not in [AppState.SHUTDOWN, AppState.PRE_INITIALIZED]:
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
                await self._set_state(AppState.INITIALIZED)

            return True

        except Exception as error:
            logger.exception(error)
            logger.error(f"[{self.name}] Component and module init failed. {error.__class__.__name__}")

            # await self._set_state(Module.AppState.ERROR)

        return False

    async def start(self, from_system=False) -> bool:
        # if self._model.state == Module.AppState.ERROR:
        #     raise MISError("Can not start module that is in 'ERROR' state")
        if not from_system and self._model.state not in [AppState.STOPPED, AppState.INITIALIZED]:
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
                await self._set_state(AppState.RUNNING)

            return True

        except Exception as error:
            logger.exception(error)
            logger.error(f"[{self.name}] Component and module start failed. {error.__class__.__name__}")

            # await self._set_state(Module.AppState.ERROR)

        return False

    async def stop(self, from_system=False) -> bool:
        # if self._model.state == Module.AppState.ERROR:
        #     raise MISError("Can not stop module that is in 'ERROR' state")
        if not from_system and self._model.state != AppState.RUNNING:
            raise MISError("Can not stop module that not in 'RUNNING' state ")

        for component in self.components:
            await component.stop()
            logger.debug(f'[{self.name}] component {component.__class__.__name__} stopped')

        if self.stop_event:
            await self.stop_event(self)

        # not change state if it is system call
        if not from_system:
            await self._set_state(AppState.STOPPED)

        return True

    async def shutdown(self, from_system=False) -> bool:
        # if self._model.state == Module.AppState.ERROR:
        #     raise MISError("Can not shutdown module that is in 'ERROR' state")
        if not from_system and self._model.state not in [AppState.STOPPED, AppState.INITIALIZED, AppState.PRE_INITIALIZED]:
            raise MISError("Can not shutdown module that not in 'STOPPED', 'INITIALIZED', 'PRE_INITIALIZED' state")

        for component in self.components:
            await component.shutdown()
            logger.debug(f'[{self.name}] component {component.__class__.__name__} shutdown finished')

        if self.shutdown_event:
            await self.shutdown_event(self)

        # not change state if it is system call
        if not from_system:
            await self._set_state(AppState.SHUTDOWN)

        return True

    async def get_context(self, user=None, team=None) -> AppContext:
        """Context for jobs and other services.
        If user or team is defined then variables will be available in context along with module variables"""
        variable_value_service = get_variable_value_service()

        return AppContext(
            module=self,
            user=user,
            team=team,
            variables=await variable_value_service.make_variable_set(user=user, team=team, app=self._model),
            routing_keys=await Eventory.make_routing_keys_set(app=self._model)
        )

    def set_manifest(self, manifest: 'ModuleManifest'):
        self.name = manifest.name
        self.display_name = manifest.display_name
        self.description = manifest.description
        self.version = manifest.version
        self.author = manifest.author
        self.category = manifest.category
        self.permissions = manifest.permissions
        self.dependencies = manifest.dependencies
        self.auth_disabled = manifest.auth_disabled
        # TODO add global_settings, local_settings
