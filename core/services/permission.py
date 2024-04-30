from core.db.models import Module
from core.db.permission import Permission
from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork


class PermissionService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.permission_repo)
        self.uow = uow

    async def create_with_scope(self, name: str, scope: str, module: Module):
        module_scope = self.make_module_scope(module_name=module.name, scope=scope)
        return await self.uow.permission_repo.create(data={
            'name': name,
            'scope': module_scope,
            'app_id': module.pk,
        })

    @staticmethod
    def make_module_scope(module_name: str, scope: str):
        return f"{module_name}:{scope}"

    async def update_or_create(self, name: str, scope: str, module: Module) -> Permission:
        async with self.uow:
            app_scope = self.make_module_scope(module_name=module.name, scope=scope)
            perm = await self.get(scope=app_scope)
            if not perm:
                perm = await self.create_with_scope(
                    scope=scope,
                    module=module,
                    name=name,
                )
            else:
                await self.uow.permission_repo.update(
                    id=perm.pk, data={'app_id': module.pk, 'name': name})
            return perm

    async def delete_unused(self, module_id: int, exist_ids: list[int]) -> int:
        """Delete unused permissions for module"""
        return await self.uow.permission_repo.delete_unused(module_id=module_id, exist_ids=exist_ids)
