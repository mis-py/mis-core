from core.db.models import User, Team
from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork


class GrantedPermissionService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.granted_permission_repo)
        self.uow = uow

    async def set_for_user(self, permissions: list, user: User):
        async with self.uow:
            for permission in permissions:
                if user.pk == 1 and permission.permission_id == 1:
                    continue

                perm = await self.uow.permission_repo.get(id=permission.permission_id)
                if not perm:
                    continue

                if permission.granted:
                    await user.add_permission(perm.scope)
                else:
                    await user.remove_permission(perm.scope)

    async def set_for_team(self, permissions: list, team: Team):
        async with self.uow:
            for permission in permissions:
                perm = await self.uow.permission_repo.get(id=permission.permission_id)
                if not perm:
                    continue

                if permission.granted:
                    await team.add_permission(perm.scope)
                else:
                    await team.remove_permission(perm.scope)
