import types
from loguru import logger
import os

from core import crud
from .utils import apps_sort_by_dependency, import_module, unload_module
from ..utils.BaseModule import BaseModule
# from .exceptions import ModuleError
# from core.db import App
from core.crud import module
from const import MODULES_DIR, MODULES_DIR_NAME

# from modules.core.notifications.handlers import eventory_message_handler
# from core.utils import async_partial
# from core.websockets.actions import Action


class ModuleService:
    _loaded_apps: dict[str, BaseModule] = {}
    # _core_consumer: Optional[Consumer]

    @classmethod
    def loaded_apps(cls):
        # MappingProxyType will allow to access members of dict but restrict their modifying
        return types.MappingProxyType(cls._loaded_apps)

    @classmethod
    async def pre_init(cls, application):
        modules_dirs = os.listdir(MODULES_DIR)
        modules = [import_module(module, MODULES_DIR_NAME) for module in modules_dirs if "__" not in module]

        # we need to load apps in specific order, so we sort it by dependency tree
        sorted_modules = apps_sort_by_dependency(modules)

        for module in sorted_modules:
            logger.debug(f'[ModuleService] Started pre init module: {module.name}')

            await cls.pre_init_module(application, module)

            logger.debug(f"[ModuleService] Module '{module.name}' pre init finished!")

    @classmethod
    async def init(cls, application):
        for module_name, module in cls._loaded_apps.items():
            logger.debug(f'[ModuleService] Started init module: {module.name}')

            is_loaded_success = await cls.init_module(application, module)

            # if is_loaded_success and app.enabled:
            #     await cls.start_app(app)
            #     logger.debug(f'[ModuleService] Module {app.name} started!')

            logger.info(f"[ModuleService] Module '{module.name}' init finished!")

        # need for start consumer for core websocket sender
        # await cls._restart_core_consumer()

    @classmethod
    async def shutdown(cls):
        """
        Executes when application shutdowns.
        Calls stop_app for every enabled app
        :return:
        """
        for module_name, module in cls._loaded_apps.items():
            logger.info(f"[ModuleService] Stopping {module.name}")
            await cls.stop_app(module_name)

    @classmethod
    async def pre_init_module(cls, application, module: BaseModule):
        if not module:
            logger.error(f"[ModuleService] Module '{module.name}' not loaded. Module not found or raised exception")
            return False

        logger.debug(f"[ModuleService] Module '{module.name}' started pre_init components.")

        try:
            for component in module.pre_init_components:
                await component.bind(module).pre_init()
                logger.debug(f'[ModuleService] component {component.__class__.__name__} for module {module.name} pre init finished')

            await module.pre_init()

        except Exception as error:
            logger.exception(error)
            logger.error(f"[ModuleService] Module '{module.name}' component not loaded. {error.__class__.__name__}")
            return False

        cls._loaded_apps[module.name] = module
        return True

    @classmethod
    async def init_module(cls, application, module: BaseModule):

        app_model, is_created = await crud.module.get_or_create(name=module.name)

        module.model = app_model

        logger.debug(f"[ModuleService] Module '{module.name}' started init components.")
        try:
            for component in module.components:
                await component.bind(module).init(application, app_model, is_created)
                logger.debug(f'[ModuleService] component {component.__class__.__name__} for module {module.name} init finished')

            await module.init()

        except Exception as error:
            logger.exception(error)
            logger.error(f"[ModuleService] Module '{module.name}' not loaded. {error.__class__.__name__}")
            return False

        module.initialized = True

        return True

    @classmethod
    async def shutdown_app(cls, app_name):
        app = cls._loaded_apps[app_name]

        # if app.name == 'core':
        #     return
        # elif app.name not in cls._loaded_apps:
        #     # await app.delete()
        #     return

        if app.enabled:
            await cls.stop_app(app)

        module = cls._loaded_apps.pop(app.name)
        for component in module.components:
            await component.shutdown()
            logger.debug(f'[{app.name}] component {component.__class__.__name__} shutdown')

        await module.shutdown()

        module.initialized = False

        unload_module(app.name)

        # await app.delete()

    @classmethod
    async def start_app(cls, app_name):
        app = cls._loaded_apps[app_name]
        try:
            for component in app.components:
                await component.start()
                logger.debug(f'[{app.name}] component {component.__class__.__name__} started')
            await app.start()
        except Exception as error:
            logger.exception(error)
            logger.error(f"Module '{app.name}' not started. {error.__class__.__name__}")
            return False

        app.enabled = True

        # await app.save()
        #
        # if app.sender:
        #     await cls._restart_core_consumer()

    @classmethod
    async def stop_app(cls, app_name):
        app = cls._loaded_apps[app_name]

        for component in app.components:
            await component.stop()
            logger.debug(f'[{app.name}] component {component.__class__.__name__} stopped')
        await app.stop()

        app.enabled = False

        # await app.save()
        # if module.sender:
        #     await cls._restart_core_consumer()

    # @classmethod
    # async def _restart_core_consumer(cls):
    #     """
    #     Create core consumer with core and modules senders
    #     """
    #     print(cls.__dict__)
    #     if cls._core_consumer:
    #         await cls._core_consumer.stop()

        # all_keys = await crud.routing_key.all_keys_values_list()
        # senders = await cls._get_all_senders()
        #
        # # TODO for what redis here?
        # message_handler_partial = async_partial(coro=eventory_message_handler, redis=RedisService)
        #
        # cls._core_consumer = await Eventory.register_handler(
        #     app_name='core',
        #     routing_keys=all_keys,
        #     callback=message_handler_partial,
        #     senders=senders,
        # )
        # await cls._core_consumer.start()

    # @classmethod
    # async def _get_all_senders(cls):
    #     senders = []
    #
    #     # append core websocket sender
    #     # ws_notify_sender = async_partial(self.misapp.ws_manager.run_action, Action.NOTIFICATIONS)
    #     # senders.append(ws_notify_sender)
    #
    #     # append modules(only enabled) senders
    #     enabled_apps = await crud_app.get_enabled_app_names()
    #     for module in cls._loaded_apps.values():
    #         if module.sender and module.name in enabled_apps:
    #             senders.append(module.sender)
    #
    #     return senders
