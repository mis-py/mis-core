from tortoise import transactions

from core.db.models import User, Team
from core.repositories.granted_permission import IGrantedPermissionRepository
from core.repositories.permission import IPermissionRepository
from core.services.base.base_service import BaseService


class GrantedPermissionService(BaseService):
    def __init__(self, granted_permission_repo: IGrantedPermissionRepository, permission_repo: IPermissionRepository):
        self.granted_permission_repo = granted_permission_repo
        self.permission_repo = permission_repo
        super().__init__(repo=granted_permission_repo)

    @transactions.atomic()
    async def set_for_user(self, permissions: list, user: User):
        for permission in permissions:
            if user.pk == 1 and permission.permission_id == 1:
                continue

            perm = await self.permission_repo.get(id=permission.permission_id)
            if not perm:
                continue

            if permission.granted:
                await user.add_permission(perm.scope)
            else:
                await user.remove_permission(perm.scope)

    @transactions.atomic()
    async def set_for_team(self, permissions: list, team: Team):
        for permission in permissions:
            perm = await self.permission_repo.get(id=permission.permission_id)
            if not perm:
                continue

            if permission.granted:
                await team.add_permission(perm.scope)
            else:
                await team.remove_permission(perm.scope)
