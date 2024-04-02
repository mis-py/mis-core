from core.db.guardian import GuardianAccessGroup
from core.exceptions import NotFound
from core.schemas.guardian import UserPermCreate, AccessGroupUpdate, GroupPermCreate, AccessGroupCreate

from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork


class GContentTypeService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.g_content_type_repo)
        self.uow = uow


class GPermissionService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.g_permission_repo)
        self.uow = uow


class GAccessGroupService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.g_access_group_repo)
        self.uow = uow

    async def create_with_users(self, name: str, users_ids: list[int] = None):
        async with self.uow:
            group = await self.uow.g_access_group_repo.create(data={'name': name})
            if users_ids:
                await self.add_users(group=group, users_ids=users_ids)
        return group

    async def add_users(self, group: GuardianAccessGroup, users_ids: list[int]):
        users = await self.uow.user_repo.find_by_ids(ids=users_ids)
        if not users:
            raise NotFound(f"None of users ids not found for add to group!")
        await self.uow.g_access_group_repo.add_users(group=group, users=users)

    async def remove_users(self, group: GuardianAccessGroup, users_ids: list[int]):
        users = await self.uow.user_repo.find_by_ids(ids=users_ids)
        if not users:
            raise NotFound(f"None of users ids not found for remove from group!")
        await self.uow.g_access_group_repo.remove_users(group=group, users=users)


class GUserPermissionService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.g_user_permission_repo)
        self.uow = uow

    async def add_user_perm(self, schema_in: UserPermCreate):
        async with self.uow:
            content_type = await self.uow.g_content_type_repo.get(id=schema_in.content_type_id)
            if content_type is None:
                raise NotFound(f"content_type_id '{schema_in.content_type_id}' not found")

            permission = await self.uow.g_permission_repo.get(id=schema_in.permission_id)
            if permission is None:
                raise NotFound(f"permission_id '{schema_in.permission_id}' not found")

            user = await self.uow.user_repo.get(id=schema_in.user_id)
            if user is None:
                raise NotFound(f"user_id '{schema_in.user_id}' not found")

            user_perm = await self.uow.g_user_permission_repo.create(data=schema_in.model_dump())
        return user_perm


class GGroupPermissionService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.g_group_permission_repo)
        self.uow = uow

    async def add_group_perm(self, schema_in: GroupPermCreate):
        async with self.uow:
            content_type = await self.uow.g_content_type_repo.get(id=schema_in.content_type_id)
            if content_type is None:
                raise NotFound(f"content_type_id '{schema_in.content_type_id}' not found")

            permission = await self.uow.g_permission_repo.get(id=schema_in.permission_id)
            if permission is None:
                raise NotFound(f"permission_id '{schema_in.permission_id}' not found")

            group = await self.uow.g_access_group_repo.get(id=schema_in.group_id)
            if group is None:
                raise NotFound(f"group_id '{schema_in.group_id}' not found")

            group_perm = await self.uow.g_group_permission_repo.create(data=schema_in.model_dump())
        return group_perm
