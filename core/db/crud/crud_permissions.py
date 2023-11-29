from core.db import Permission, GrantedPermission, App
from core.db.crud.base import CRUDBase


class CRUDPermission(CRUDBase):
    async def update_or_create(self, app: App, scope: str, name: str) -> Permission:
        app_scope = self.model.make_app_scope(app_name=app.name, scope=scope)
        perm = await self.get(scope=app_scope)
        if not perm:
            perm = await self.model.create(
                scope=scope,
                app=app,
                name=name,
            )
        else:
            perm.app = app
            perm.name = name
            await perm.save()
        return perm

    async def update_name(self, perm: Permission, name: str):
        """Update name if old name not equal new name"""
        if perm.name != name:
            perm.name = name
            await perm.save()
        return perm

    async def remove_unused(self, app: App, exist_ids: list[int]) -> int:
        """Remove unused permissions for app"""
        return await self.model.filter(app=app).exclude(id__in=exist_ids).delete()


crud_permission = CRUDPermission(Permission)


class CRUDGrantedPermission(CRUDBase):
    pass


granted_permission = CRUDGrantedPermission(GrantedPermission)
