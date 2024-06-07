from loguru import logger

from core.db.dataclass import AppState
from core.db.models import Module
from core.dependencies.services import get_variable_service
from core.exceptions import MISError
from core.repositories.module import IModuleRepository
from core.schemas.module import ModuleManifestResponse, ModuleManifest
from core.services.base.base_service import BaseService
from core.utils.module import LoadedModule, GenericModule, AppContext
from core.utils.module.utils import unload_module
from core.utils.schema import PageResponse
from libs.eventory import Eventory


class ModuleService(BaseService):
    _loaded_modules: dict[str, LoadedModule] = {}
    _manifests: dict[str, ModuleManifest]
    # _core_consumer: Optional[Consumer]

    def __init__(self, module_repo: IModuleRepository):
        self.module_repo = module_repo
        super().__init__(repo=module_repo)

    @classmethod
    def add_manifest(cls, module_name: str, manifest: ModuleManifest):
        if module_name not in cls._loaded_modules:
            cls._loaded_modules[module_name] = LoadedModule(manifest=manifest)

    @classmethod
    def add_instance(cls, module_name: str, instance: GenericModule):
        if module_name in cls._loaded_modules:
            cls._loaded_modules[module_name].instance = instance
            instance.set_manifest(cls._loaded_modules[module_name].manifest)

    @classmethod
    def get_manifest(cls, module_name):
        # return read_module_manifest(module_name)
        return cls._manifests[module_name]

    @classmethod
    def get_loaded_module(cls, module_name: str) -> LoadedModule:
        if module_name == 'core':
            raise MISError("Operations on 'core' module not allowed from 'module_service'")

        if module_name not in cls._loaded_modules:
            raise MISError(f"Module '{module_name}' not registered in 'module_service'")

        return cls._loaded_modules[module_name]

    @classmethod
    def get_loaded_module_names(cls) -> list[str]:
        return list(cls._loaded_modules.keys())

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

        loaded_module = cls.get_loaded_module(module_name)
        logger.debug(f'[ModuleService] Module: {module_name} init started!')

        init_result = await loaded_module.instance.init()

        logger.debug(f'[ModuleService] Module: {module_name} init finished: {init_result}!')

        return loaded_module.instance

    @classmethod
    async def start_module(cls, module_name: str) -> GenericModule:
        loaded_module = cls.get_loaded_module(module_name)

        await loaded_module.instance.start()

        logger.debug(f'[ModuleService] Module: {module_name} started!')

        # if app.sender:
        #     await cls._restart_core_consumer()

        return loaded_module.instance

    @classmethod
    async def stop_module(cls, module_name: str) -> GenericModule:
        loaded_module = cls.get_loaded_module(module_name)

        await loaded_module.instance.stop()

        logger.debug(f"[ModuleService] Module: {module_name} stopped")

        # if module.sender:
        #     await cls._restart_core_consumer()

        return loaded_module.instance

    @classmethod
    async def shutdown_module(cls, module_name: str, from_system=False):
        loaded_module = cls.get_loaded_module(module_name)
        await loaded_module.instance.shutdown()

        if from_system:
            # correctly unload and delete module from system call
            unload_module(module_name)
            del cls._loaded_modules[module_name]

        logger.debug(f"[ModuleService] Module: {module_name} shutdown complete")

    @classmethod
    async def refresh_from_db(cls, module_name: str,):
        loaded_module = cls.get_loaded_module(module_name)
        await loaded_module.instance.refresh_from_db()

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

    async def set_manifest_in_response(self, paginated_modules: PageResponse[ModuleManifestResponse]):
        for module in paginated_modules.result.items:
            if module.name == 'core':  # skip module without manifest
                continue

            module.manifest = self.get_manifest(module.name)
        return paginated_modules

    async def set_state(self, module_id: int, state: AppState) -> None:
        updated_obj = await self.module_repo.update(
            id=module_id,
            data={'state': state},
        )

        await updated_obj.save()

    async def init(self, module_id: int):
        module_obj: Module = await self.module_repo.get(id=module_id)

        if module_obj.state not in [AppState.SHUTDOWN, AppState.PRE_INITIALIZED]:
            raise MISError("Can not init module that is not in 'SHUTDOWN' or 'PRE_INITIALIZED' or 'ERROR' state")

        success = self.init_module(module_obj.name)

        if not success:
            # await self.set_state(module_id=module_id, state=AppState.ERROR)
            raise MISError("Module init is not success")

        await self.set_state(module_id=module_id, state=AppState.INITIALIZED)

        await self.refresh_from_db(module_obj.name)
        # TODO verify is it needed to refresh again here?
        await module_obj.refresh_from_db()

    async def start(self, module_id: int):
        module_obj: Module = await self.module_repo.get(id=module_id)
        # if self._model.state == Module.AppState.ERROR:
        #     raise MISError("Can not start module that is in 'ERROR' state")
        if module_obj.state not in [AppState.STOPPED, AppState.INITIALIZED]:
            raise MISError("Can not start module that not in 'STOPPED' or 'INITIALIZED' state ")

        success = self.start_module(module_obj.name)

        if not success:
            # await self._set_state(Module.AppState.ERROR)
            raise MISError("Module start is not success")

        await self.set_state(module_id=module_id, state=AppState.RUNNING)
        await self.set_enabled(module_id=module_id)

        await self.refresh_from_db(module_obj.name)

    async def stop(self, module_id: int):
        module_obj: Module = await self.module_repo.get(id=module_id)
        # if self._model.state == Module.AppState.ERROR:
        #     raise MISError("Can not stop module that is in 'ERROR' state")
        if module_obj.state != AppState.RUNNING:
            raise MISError("Can not stop module that not in 'RUNNING' state ")

        success = self.stop_module(module_obj.name)

        await self.set_state(module_id=module_id, state=AppState.STOPPED)
        await self.set_disabled(module_id=module_id)

        await self.refresh_from_db(module_obj.name)

    async def shutdown(self, module_id: int):
        module_obj: Module = await self.module_repo.get(id=module_id)
        # if self._model.state == Module.AppState.ERROR:
        #     raise MISError("Can not shutdown module that is in 'ERROR' state")
        if module_obj.state not in [AppState.STOPPED, AppState.INITIALIZED, AppState.PRE_INITIALIZED]:
            raise MISError("Can not shutdown module that not in 'STOPPED', 'INITIALIZED', 'PRE_INITIALIZED' state")

        success = self.shutdown_module(module_obj.name)

        await self.set_state(module_id=module_id, state=AppState.SHUTDOWN)

        await self.refresh_from_db(module_obj.name)

    async def set_enabled(self, module_id: int):
        updated_obj = await self.module_repo.update(
            id=module_id,
            data={'enabled': True},
        )

        await updated_obj.save()

        return await self.module_repo.get(id=module_id)

    async def set_disabled(self, module_id: int):
        updated_obj = await self.module_repo.update(
            id=module_id,
            data={'enabled': False},
        )

        await updated_obj.save()

    async def get_or_create(self, name: str):
        return await self.module_repo.get_or_create_by_name(name=name)

    async def create_core(self, name: str):
        """Create core app as enabled and already running"""
        return await self.module_repo.create(data={
            'name': name,
            'enabled': True,
            'state': AppState.RUNNING,
        })

    @staticmethod
    async def get_app_context(app: Module, user=None, team=None):
        variable_service = get_variable_service()
        return AppContext(
            user=user,
            team=team,
            variables=await variable_service.make_variable_set(user=user, team=user.team, app=app),
            app_name=app.name,
            routing_keys=await Eventory.make_routing_keys_set(app=app)
        )