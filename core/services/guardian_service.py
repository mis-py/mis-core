from tortoise.transactions import in_transaction

from core.db.guardian import GuardianAccessGroup
from core.db.models import User
from core.exceptions import NotFound, ValidationFailed
from core.repositories.guardian_access_group import IGAccessGroupRepository
from core.repositories.guardian_content_type import IGContentTypeRepository
from core.repositories.guardian_group_permission import IGGroupPermissionRepository
from core.repositories.guardian_permission import IGPermissionRepository
from core.repositories.guardian_user_permission import IGUserPermissionRepository
from core.repositories.user import IUserRepository
from core.schemas.guardian import UserPermCreate, GroupPermCreate

from core.services.base.base_service import BaseService


class GContentTypeService(BaseService):
    def __init__(self, g_content_type_repo: IGContentTypeRepository):
        self.g_content_type_repo = g_content_type_repo
        super().__init__(repo=g_content_type_repo)


class GPermissionService(BaseService):
    def __init__(self, g_permission_repo: IGPermissionRepository):
        self.g_permission_repo = g_permission_repo
        super().__init__(repo=g_permission_repo)


class GAccessGroupService(BaseService):
    def __init__(self, g_access_group_repo: IGAccessGroupRepository, user_repo: IUserRepository):
        self.g_access_group_repo = g_access_group_repo
        self.user_repo = user_repo
        super().__init__(repo=g_access_group_repo)

    async def create_with_users(self, name: str, users_ids: list[int] = None):
        async with in_transaction():
            group = await self.g_access_group_repo.create(data={'name': name})
            if users_ids:
                await self.add_users(group=group, users_ids=users_ids)
        return group

    async def add_users(self, group: GuardianAccessGroup, users_ids: list[int]):
        users = await self.user_repo.find_by_ids(ids=users_ids)
        if not users:
            raise NotFound(f"None of users ids not found for add to group!")
        await self.g_access_group_repo.add_users(group=group, users=users)

    async def remove_users(self, group: GuardianAccessGroup, users_ids: list[int]):
        users = await self.user_repo.find_by_ids(ids=users_ids)
        if not users:
            raise NotFound(f"None of users ids not found for remove from group!")
        await self.g_access_group_repo.remove_users(group=group, users=users)


class GUserPermissionService(BaseService):
    def __init__(
            self,
            g_user_permission_repo: IGUserPermissionRepository,
            g_content_type_repo: IGContentTypeRepository,
            g_permission_repo: IGPermissionRepository,
            user_repo: IUserRepository,
    ):
        self.g_user_permission_repo = g_user_permission_repo
        self.g_content_type_repo = g_content_type_repo
        self.g_permission_repo = g_permission_repo
        self.user_repo = user_repo
        super().__init__(repo=g_user_permission_repo)

    async def add_user_perm(self, schema_in: UserPermCreate):
        async with in_transaction():
            content_type = await self.g_content_type_repo.get(id=schema_in.content_type_id)
            if content_type is None:
                raise NotFound(f"content_type_id '{schema_in.content_type_id}' not found")

            permission = await self.g_permission_repo.get(id=schema_in.permission_id)
            if permission is None:
                raise NotFound(f"permission_id '{schema_in.permission_id}' not found")

            user = await self.user_repo.get(id=schema_in.user_id)
            if user is None:
                raise NotFound(f"user_id '{schema_in.user_id}' not found")

            user_perm = await self.g_user_permission_repo.create(data=schema_in.model_dump())
        return user_perm


class GGroupPermissionService(BaseService):
    def __init__(
            self,
            g_group_permission_repo: IGGroupPermissionRepository,
            g_content_type_repo: IGContentTypeRepository,
            g_permission_repo: IGPermissionRepository,
            g_access_group_repo: IGAccessGroupRepository,
            user_repo: IUserRepository,
    ):
        self.g_group_permission_repo = g_group_permission_repo
        self.g_content_type_repo = g_content_type_repo
        self.g_permission_repo = g_permission_repo
        self.g_access_group_repo = g_access_group_repo
        self.user_repo = user_repo
        super().__init__(repo=g_group_permission_repo)

    async def add_group_perm(self, schema_in: GroupPermCreate):
        async with in_transaction():
            content_type = await self.g_content_type_repo.get(id=schema_in.content_type_id)
            if content_type is None:
                raise NotFound(f"content_type_id '{schema_in.content_type_id}' not found")

            permission = await self.g_permission_repo.get(id=schema_in.permission_id)
            if permission is None:
                raise NotFound(f"permission_id '{schema_in.permission_id}' not found")

            group = await self.g_access_group_repo.get(id=schema_in.group_id)
            if group is None:
                raise NotFound(f"group_id '{schema_in.group_id}' not found")

            group_perm = await self.g_group_permission_repo.create(data=schema_in.model_dump())
        return group_perm


class GuardianService:
    def __init__(
            self,
            g_group_permission_repo: IGGroupPermissionRepository,
            g_user_permission_repo: IGUserPermissionRepository,
            g_content_type_repo: IGContentTypeRepository,
            g_permission_repo: IGPermissionRepository,
            g_access_group_repo: IGAccessGroupRepository,
    ):
        self.g_group_permission_repo = g_group_permission_repo
        self.g_user_permission_repo = g_user_permission_repo
        self.g_content_type_repo = g_content_type_repo
        self.g_permission_repo = g_permission_repo
        self.g_access_group_repo = g_access_group_repo

    async def assign_perm(self, perm: str, user_or_group: User | GuardianAccessGroup, obj):
        """Assign object permission to user or group"""

        class_name = obj.__class__.__name__
        content_type = await self.g_content_type_repo.get(model=class_name)
        if not content_type:
            raise NotFound('Content type not found')

        permission = await self.g_permission_repo.get(code_name=perm, content_type=content_type)
        if not permission:
            raise NotFound('Permission not found')

        if isinstance(user_or_group, User):
            user = user_or_group
            return await self.g_user_permission_repo.get_or_create(
                user_id=user.pk,
                permission_id=permission.pk,
                content_type_id=content_type.pk,
                object_pk=obj.id,
            )
        elif isinstance(user_or_group, GuardianAccessGroup):
            group = user_or_group
            return await self.g_group_permission_repo.get_or_create(
                group_id=group.pk,
                permission_id=permission.pk,
                content_type_id=content_type.pk,
                object_pk=obj.id,
            )
        else:
            raise ValidationFailed("user_or_group is not User or AccessGroup")

    async def has_perm(self, perm: str, user_or_group: User | GuardianAccessGroup, obj) -> bool:
        """User or Group permission checker"""

        model = obj.__class__.__name__
        object_pk = obj.id
        if isinstance(user_or_group, User):
            user = user_or_group
            perms = await self._get_user_perms(user=user, model=model, object_pk=object_pk)
        elif isinstance(user_or_group, GuardianAccessGroup):
            group = user_or_group
            perms = await self._get_group_perm(group=group, model=model, object_pk=object_pk)
        else:
            raise Exception("user_or_group is not User or AccessGroup")

        return perm in perms

    async def _get_user_perms(self, user: User, model: str, object_pk: str):
        """Get user permission code names. Compared with groups permission code names"""

        groups = await user.access_groups.all()
        groups_ids = [group.id for group in groups]
        user_perms = await self.g_permission_repo.users_perms_list(
            user_id=user.pk, model=model, object_pk=object_pk)
        if groups:
            groups_perms = await self.g_permission_repo.multi_group_perms_list(
                model=model, groups_ids=groups_ids, object_pk=object_pk,
            )
            user_perms.extend(groups_perms)
        return user_perms

    async def _get_group_perm(self, group: GuardianAccessGroup, model: str, object_pk: str):
        """Get group permission code names"""
        group_perms = await self.g_permission_repo.group_perms_list(
            model=model,
            group_id=group.pk,
            object_pk=object_pk
        )
        return group_perms

    async def get_user_assigned_objects(self, perm: str, queryset, user: User):
        """Return filtered queryset by permission"""
        all_objects_pks = []

        # collect user permission objects
        user_perm_objects_pks = await self.g_user_permission_repo.get_objects_pks()
        all_objects_pks.extend(user_perm_objects_pks)

        # collect groups permission objects
        groups = await user.access_groups.all()
        if groups:
            groups_ids = [group.id for group in groups]
            groups_perm_objects_pks = await self.g_group_permission_repo.get_objects_pks_by_multi_groups(
                groups_ids=groups_ids, perm=perm, model=queryset.model.__name__
            )
            all_objects_pks.extend(groups_perm_objects_pks)

        return await queryset.filter(id__in=all_objects_pks)

    async def get_group_assigned_objects(self, perm: str, queryset, group: GuardianAccessGroup):
        """Return filtered queryset by permission"""
        objects_pks = await self.g_group_permission_repo.get_objects_pks(
            group_id=group.pk, perm=perm, model=queryset.model.__name__
        )
        return await queryset.filter(id__in=objects_pks)
