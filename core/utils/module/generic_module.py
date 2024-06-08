from loguru import logger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.schemas.module import ModuleManifest

from .Base.BaseModule import BaseModule


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

    async def pre_init(self, application) -> bool:
        """
        pre_init calls automatically on system startup
        """
        try:
            for component in self.pre_init_components:
                await component.bind(self).pre_init(application)
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

    async def init(self) -> bool:
        try:
            for component in self.components:
                await component.init(self._model, self._is_created)
                logger.debug(f'[{self.name}] component {component.__class__.__name__} init finished')

            if self.init_event:
                await self.init_event(self)

            return True

        except Exception as error:
            logger.exception(error)
            logger.error(f"[{self.name}] Component and module init failed. {error.__class__.__name__}")

        return False

    async def start(self) -> bool:
        try:
            for component in self.components:
                await component.start()
                logger.debug(f'[{self.name}] component {component.__class__.__name__} started')

            if self.start_event:
                await self.start_event(self)

            return True

        except Exception as error:
            logger.exception(error)
            logger.error(f"[{self.name}] Component and module start failed. {error.__class__.__name__}")

        return False

    async def stop(self) -> bool:
        for component in self.components:
            await component.stop()
            logger.debug(f'[{self.name}] component {component.__class__.__name__} stopped')

        if self.stop_event:
            await self.stop_event(self)

        return True

    async def shutdown(self) -> bool:
        for component in self.components:
            await component.shutdown()
            logger.debug(f'[{self.name}] component {component.__class__.__name__} shutdown finished')

        if self.shutdown_event:
            await self.shutdown_event(self)

        return True

    async def refresh_from_db(self) -> bool:
        await self._model.refresh_from_db()
        return True

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
