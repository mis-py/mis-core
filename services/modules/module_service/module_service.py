import types
from loguru import logger
import os

from core import crud
from core.services.base.unit_of_work import unit_of_work_factory
from core.services.module import ModuleUOWService
from .utils import manifests_sort_by_dependency, import_module, unload_module, read_module_manifest, \
    module_dependency_check
from ..utils import ModuleTemplate
from ..utils.BaseModule import BaseModule
# from .exceptions import ModuleError
# from core.db import App
from const import MODULES_DIR, MODULES_DIR_NAME
from ..utils.manifest import ModuleManifest


# from modules.core.notifications.handlers import eventory_message_handler
# from core.utils import async_partial
# from core.websockets.actions import Action


class ModuleService:
    _modules_manifests: dict[str, ModuleManifest] = {}
    _loaded_modules: dict[str, ModuleTemplate] = {}

    # _core_consumer: Optional[Consumer]

    @classmethod
    def loaded_modules(cls):
        # MappingProxyType will allow to access members of dict but restrict their modifying
        return types.MappingProxyType(cls._loaded_modules)

    @classmethod
    async def manifest_init(cls, application):
        # collect manifest.json files from each module in modules directory
        manifests = {}
        for module in os.listdir(MODULES_DIR):
            if "__" in module:
                continue
            manifest = read_module_manifest(module)

            if not manifest:
                continue
            manifests[module] = manifest

        # we need to load modules in specific order, so we sort it by dependency tree
        sorted_module_manifests = manifests_sort_by_dependency(manifests)

        # validation dependency version
        for module_name, manifest in sorted_module_manifests.items():
            is_valid_dependency_version = module_dependency_check(
                module_manifest=manifest, all_manifests=sorted_module_manifests
            )
            if not is_valid_dependency_version:
                continue

            cls._modules_manifests[manifest.name] = manifest

    @classmethod
    async def pre_init(cls, application):
        # import modules by sorted manifests and run pre init for each module
        for manifest in cls._modules_manifests.values():
            module = import_module(manifest.name, MODULES_DIR_NAME)
            module.module.set_manifest(manifest)

            logger.debug(f'[ModuleService] Started pre init module: {manifest.name}')
            await cls.pre_init_module(application, module.module)
            logger.debug(f"[ModuleService] Module '{manifest.name}' pre init finished!")

    @classmethod
    async def init(cls, application):
        module_uow_service = ModuleUOWService(unit_of_work_factory())
        for module_name, module in cls._loaded_modules.items():
            logger.debug(f'[ModuleService] Started init module: {module.name}')

            is_loaded_success = await cls.init_module(application, module, module_uow_service)

            if is_loaded_success and module.model.enabled:
                await cls.start_module(module.name, module_uow_service)
                logger.debug(f'[ModuleService] Module {module.name} started!')

            logger.info(f"[ModuleService] Module '{module.name}' init finished!")

        # need for start consumer for core websocket sender
        # await cls._restart_core_consumer()

    @classmethod
    async def shutdown(cls):
        """
        Executes when application shutdowns.
        Calls stop_module for every enabled app
        :return:
        """
        for module_name, module in cls._loaded_modules.items():
            logger.info(f"[ModuleService] Stopping {module.name}")
            await cls.stop_module(module_name)

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

        cls._loaded_modules[module.name] = module
        return True

    @classmethod
    async def init_module(cls, application, module: BaseModule, module_uow_service: ModuleUOWService):

        module_model, is_created = await module_uow_service.get_or_create(name=module.name)

        module.model = module_model

        logger.debug(f"[ModuleService] Module '{module.name}' started init components.")
        try:
            for component in module.components:
                await component.bind(module).init(application, module_model, is_created)
                logger.debug(f'[ModuleService] component {component.__class__.__name__} for module {module.name} init finished')

            await module.init()

        except Exception as error:
            logger.exception(error)
            logger.error(f"[ModuleService] Module '{module.name}' not loaded. {error.__class__.__name__}")
            return False

        module.initialized = True

        return True

    @classmethod
    async def shutdown_module(cls, module_name: str, module_uow_service: ModuleUOWService):
        module = cls._loaded_modules.pop(module_name)

        # if app.name == 'core':
        #     return
        # elif app.name not in cls._loaded_modules:
        #     # await app.delete()
        #     return

        if module.model.enabled:
            await cls.stop_module(module.name, module_uow_service=module_uow_service)

        for component in module.components:
            await component.shutdown()
            logger.debug(f'[{module.name}] component {component.__class__.__name__} shutdown')

        await module.shutdown()

        module.initialized = False

        unload_module(module.name)

        # await app.delete()

    @classmethod
    async def start_module(cls, module_name: str, uow_service: ModuleUOWService):
        module = cls._loaded_modules[module_name]
        try:
            for component in module.components:
                await component.start()
                logger.debug(f'[{module.name}] component {component.__class__.__name__} started')
            await module.start()
        except Exception as error:
            logger.exception(error)
            logger.error(f"Module '{module.name}' not started. {error.__class__.__name__}")
            return False

        await uow_service.set_enabled(module_id=module.model.pk)
        # if app.sender:
        #     await cls._restart_core_consumer()

    @classmethod
    async def stop_module(cls, module_name: str, module_uow_service: ModuleUOWService):
        module = cls._loaded_modules[module_name]

        for component in module.components:
            await component.stop()
            logger.debug(f'[{module.name}] component {component.__class__.__name__} stopped')
        await module.stop()

        await module_uow_service.set_disabled(module_id=module.model.pk)
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
