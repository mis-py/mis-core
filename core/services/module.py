from core.db.models import Module
from core.repositories.module import IModuleRepository
from core.schemas.module import ModuleManifestResponse
from core.services.base.base_service import BaseService
from core.utils.schema import PageResponse
from services.modules.module_service.utils import read_module_manifest


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
            'state': Module.AppState.RUNNING,
        })
