from fastapi_pagination import Page
from core.schemas.module import ModuleManifestResponse
from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork
from services.modules.module_service.utils import read_module_manifest


class ModuleUOWService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.module_repo)
        self.uow = uow

    async def set_matifest_in_response(self, paginated_modules: Page[ModuleManifestResponse]):
        for module in paginated_modules.items:
            if module.name == 'core':  # skip module without manifest
                continue

            module.manifest = read_module_manifest(module.name)
        return paginated_modules

    async def set_enabled(self, module_id: int):
        await self.uow.module_repo.update(
            id=module_id,
            data={'enabled': True},
        )

    async def set_disabled(self, module_id: int):
        await self.uow.module_repo.update(
            id=module_id,
            data={'enabled': False},
        )

    async def get_or_create(self, name: str):
        return await self.uow.module_repo.get_or_create_by_name(name=name)
