from core.db.dataclass import AppState
from core.db.models import Module
from core.exceptions import MISError
from core.repositories.module import IModuleRepository
from core.schemas.module import ModuleManifestResponse
from core.services.base.base_service import BaseService
from core.utils.schema import PageResponse
from core.dependencies.services import get_variable_service
from libs.modules.AppContext import AppContext
from libs.modules.module_service.utils import read_module_manifest
from libs.modules.module_service import Modulery
from libs.eventory import Eventory


class ModuleService(BaseService):
    def __init__(self, module_repo: IModuleRepository):
        self.module_repo = module_repo
        super().__init__(repo=module_repo)

    async def set_manifest_in_response(self, paginated_modules: PageResponse[ModuleManifestResponse]):
        for module in paginated_modules.result.items:
            if module.name == 'core':  # skip module without manifest
                continue

            module.manifest = read_module_manifest(module.name)
        return paginated_modules

    def get_manifest(self, module_name):
        return read_module_manifest(module_name)

    async def set_state(self, module_id: int, state: AppState) -> None:
        updated_obj = await self.module_repo.update(
            id=module_id,
            data={'state': state},
        )

        await updated_obj.save()

        return await self.module_repo.get(id=module_id)

    async def init(self, module_id: int):
        module_obj: Module = await self.module_repo.get(id=module_id)

        if module_obj.state not in [AppState.SHUTDOWN, AppState.PRE_INITIALIZED]:
            raise MISError("Can not init module that is not in 'SHUTDOWN' or 'PRE_INITIALIZED' or 'ERROR' state")

        success = Modulery.init_module(module_obj.name)

        if not success:
            # await self.set_state(module_id=module_id, state=AppState.ERROR)
            raise MISError("Module init is not success")

        await self.set_state(module_id=module_id, state=AppState.INITIALIZED)

    async def start(self, module_id: int):
        module_obj: Module = await self.module_repo.get(id=module_id)
        # if self._model.state == Module.AppState.ERROR:
        #     raise MISError("Can not start module that is in 'ERROR' state")
        if module_obj.state not in [AppState.STOPPED, AppState.INITIALIZED]:
            raise MISError("Can not start module that not in 'STOPPED' or 'INITIALIZED' state ")

        success = Modulery.start_module(module_obj.name)

        if not success:
            # await self._set_state(Module.AppState.ERROR)
            raise MISError("Module start is not success")

        await self.set_state(module_id=module_id, state=AppState.RUNNING)
        await self.set_enabled(module_id=module_id)

        # TODO rebind needed?
        # rebind new model to module after update
        await loaded_module.instance.bind_model(new_model, False)

    async def stop(self, module_id: int):
        module_obj: Module = await self.module_repo.get(id=module_id)
        # if self._model.state == Module.AppState.ERROR:
        #     raise MISError("Can not stop module that is in 'ERROR' state")
        if module_obj.state != AppState.RUNNING:
            raise MISError("Can not stop module that not in 'RUNNING' state ")

        success = Modulery.stop_module(module_obj.name)

        await self.set_state(module_id=module_id, state=AppState.STOPPED)
        await self.set_disabled(module_id=module_id)
        # rebind new model to module after update
        await loaded_module.instance.bind_model(new_model, False)

    async def shutdown(self, module_id: int):
        module_obj: Module = await self.module_repo.get(id=module_id)
        # if self._model.state == Module.AppState.ERROR:
        #     raise MISError("Can not shutdown module that is in 'ERROR' state")
        if module_obj.state not in [AppState.STOPPED, AppState.INITIALIZED, AppState.PRE_INITIALIZED]:
            raise MISError("Can not shutdown module that not in 'STOPPED', 'INITIALIZED', 'PRE_INITIALIZED' state")

        success = Modulery.shutdown_module(module_obj.name)

        await self.set_state(module_id=module_id, state=AppState.SHUTDOWN)

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

        return await self.module_repo.get(id=module_id)

    async def get_or_create(self, name: str):
        return await self.module_repo.get_or_create_by_name(name=name)

    async def create_core(self, name: str):
        """Create core app as enabled and already running"""
        return await self.module_repo.create(data={
            'name': name,
            'enabled': True,
            'state': AppState.RUNNING,
        })

    async def make_module_context(self, module_name: str, user=None, team=None) -> AppContext:

        loaded_module = Modulery.get_module(module_name)
        """Context for jobs and other services.
        If user or team is defined then variables will be available in context along with module variables"""

        variable_service = get_variable_service()

        return AppContext(
            module=loaded_module.instance,
            user=user,
            team=team,
            variables=await variable_service.make_variable_set(user=user, team=team, app=loaded_module.model),
            routing_keys=await Eventory.make_routing_keys_set(app=loaded_module.model)
        )
