from tortoise.transactions import in_transaction

from core.db.models import Module
from core.db.permission import Permission
from core.repositories.permission import IPermissionRepository
from core.services.base.base_service import BaseService


class PermissionService(BaseService):
    def __init__(self, permission_repo: IPermissionRepository):
        self.permission_repo = permission_repo
        super().__init__(repo=permission_repo)

    async def create_with_scope(self, name: str, scope: str, module: Module):
        module_scope = self.make_module_scope(module_name=module.name, scope=scope)
        return await self.permission_repo.create(data={
            'name': name,
            'scope': module_scope,
            'app_id': module.pk,
        })

    @staticmethod
    def make_module_scope(module_name: str, scope: str):
        return f"{module_name}:{scope}"

    async def update_or_create(self, name: str, scope: str, module: Module) -> Permission:
        async with in_transaction():
            app_scope = self.make_module_scope(module_name=module.name, scope=scope)
            perm = await self.get(scope=app_scope)
            if not perm:
                perm = await self.create_with_scope(
                    scope=scope,
                    module=module,
                    name=name,
                )
            else:
                await self.permission_repo.update(
                    id=perm.pk, data={'app_id': module.pk, 'name': name})
            return perm

    async def delete_unused(self, module_id: int, exist_ids: list[int]) -> int:
        """Delete unused permissions for module"""
        return await self.permission_repo.delete_unused(module_id=module_id, exist_ids=exist_ids)
