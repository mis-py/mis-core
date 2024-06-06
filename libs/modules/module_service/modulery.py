from dataclasses import dataclass
import types
from loguru import logger
import os
from typing import Optional

from core.db.dataclass import AppState
from core.db.models import Module
from core.dependencies.services import get_module_service
from core.exceptions import MISError
from .utils import manifests_sort_by_dependency, import_module, unload_module, read_module_manifest, \
    module_dependency_check
from ..GenericModule import GenericModule
from const import MODULES_DIR, MODULES_DIR_NAME
from ..utils.ModuleManifest import ModuleManifest


# from modules.core.notifications.handlers import eventory_message_handler
# from core.utils import async_partial
# from core.websockets.actions import Action

@dataclass
class LoadedModule:
    manifest: ModuleManifest
    instance: Optional[GenericModule] = None


class Modulery:
    _modules_manifests: dict[str, ModuleManifest] = {}
    _loaded_modules: dict[str, LoadedModule] = {}

    # _core_consumer: Optional[Consumer]

    @classmethod
    def get_module(cls, module_name: str) -> LoadedModule:
        if module_name == 'core':
            raise MISError("Operations on 'core' module not allowed from 'module_service'")

        if module_name not in cls._loaded_modules:
            raise MISError(f"Module '{module_name}' not registered in 'module_service'")

        return cls._loaded_modules[module_name]

    @classmethod
    async def manifest_init(cls) -> None:
        """
        Method called by system loader!
        Collect manifest.json files from each module in modules directory
        """
        manifests = {}
        for module in os.listdir(MODULES_DIR):
            if "__" in module:
                continue
            manifest = read_module_manifest(module)

            if not manifest:
                continue
            manifests[module] = manifest

        # we need to load modules in specific order, so we sort it by dependency tree
        # sort func adds module that not exist
        sorted_module_manifests = manifests_sort_by_dependency(manifests)

        # validation dependency version
        for module_name, manifest in sorted_module_manifests.items():
            is_valid_dependency_version = module_dependency_check(
                module_manifest=manifest, all_manifests=sorted_module_manifests
            )
            if not is_valid_dependency_version:
                continue

            cls._loaded_modules[manifest.name] = LoadedModule(manifest=manifest)

    @classmethod
    async def pre_init(cls, application):
        """
        Method called by system loader!
        Import modules by sorted manifests and run pre init for each module
        """
        for module_name, loaded_module in cls._loaded_modules.items():
            package = import_module(module_name, MODULES_DIR_NAME)
            instance = package.module
            instance.set_manifest(loaded_module.manifest)

            logger.debug(f'[ModuleService] Module: {module_name} pre_init started!')
            await instance.pre_init(application)
            cls._loaded_modules[module_name].instance = instance
            logger.debug(f"[ModuleService] Module: '{module_name}' pre_init finished!")

    @classmethod
    async def init(cls):
        """
        Method called by system loader!
        Run module init and start if module is enabled
        """
        for module_name, loaded_module in cls._loaded_modules.items():
            if loaded_module.instance.is_enabled():
                try:
                    await cls.init_module(module_name, from_system=True)
                except Exception as e:
                    logger.error(f'[ModuleService] Module: {module_name} system init failed ({e}), skip...')
                    continue

                logger.debug(f'[ModuleService] Module: {module_name} auto-start is enabled starting...')

                try:
                    await cls.start_module(module_name, from_system=True)
                except Exception as e:
                    logger.error(f'[ModuleService] Module: {module_name} system init failed ({e}), skip...')
                    continue

        # need for start consumer for core websocket sender
        # await cls._restart_core_consumer()

    @classmethod
    async def shutdown(cls):
        """
        Method called by system loader!
        Executes when application shutdowns.
        Calls stop_module for every enabled app if enabled and then shutdown
        """
        for module_name, loaded_module in cls._loaded_modules.copy().items():
            if loaded_module.instance.is_enabled():
                await cls.stop_module(module_name, from_system=True)
            await cls.shutdown_module(module_name, from_system=True)

    @classmethod
    async def init_module(cls, module_name: str) -> GenericModule:

        # except ModuleNotFoundError as e:
        #     logger.exception(e)
        #     raise LoadModuleError(
        #         "App name is wrong, or app is not loaded into 'modules' directory")
        #
        # except tortoise.exceptions.ConfigurationError as e:
        # raise LoadModuleError(
        #     f"Loaded app have wrong configuration. Details: {' '.join(e.args)}")
        #
        # except Exception as e:
        # logger.exception(e)
        # raise LoadModuleError(f"Error while loading app. Details: {str(e)}")

        loaded_module = cls.get_module(module_name)
        logger.debug(f'[ModuleService] Module: {module_name} init started!')

        init_result = await loaded_module.instance.init()

        logger.debug(f'[ModuleService] Module: {module_name} init finished: {init_result}!')

        return loaded_module.instance

    @classmethod
    async def start_module(cls, module_name: str, from_system=False) -> GenericModule:
        loaded_module = cls.get_module(module_name)

        await loaded_module.instance.start(from_system)

        logger.debug(f'[ModuleService] Module: {module_name} started!')

        # if app.sender:
        #     await cls._restart_core_consumer()

        return loaded_module.instance

    @classmethod
    async def stop_module(cls, module_name: str, from_system=False) -> GenericModule:
        loaded_module = cls.get_module(module_name)

        await loaded_module.instance.stop(from_system)

        logger.debug(f"[ModuleService] Module: {module_name} stopped")

        # if module.sender:
        #     await cls._restart_core_consumer()

        return loaded_module.instance

    @classmethod
    async def shutdown_module(cls, module_name: str, from_system=False):
        loaded_module = cls.get_module(module_name)
        await loaded_module.instance.shutdown(from_system)

        if from_system:
            # correctly unload and delete module from system call
            unload_module(module_name)
            del cls._loaded_modules[module_name]

        logger.debug(f"[ModuleService] Module: {module_name} shutdown complete")


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
