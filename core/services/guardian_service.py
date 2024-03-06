from core import crud
from core.db.guardian import GuardianContentType, GuardianPermission, GuardianAccessGroup, GuardianUserPermission, \
    GuardianGroupPermission
from core.db.models import Module
from core.schemas.guardian import CreateUserPerm, UpdateAccessGroup, CreateGroupPerm


async def get_list_content_type(pagination: dict, module_id: int = None, model: str = None) -> list[GuardianContentType]:
    queryset = await crud.guardian_content_type.query_get_multi(
        **pagination,
        module_id=module_id,
        model=model,
    )
    queryset = await crud.guardian_content_type.join_module(queryset)
    return await queryset


async def get_list_permission(pagination: dict, content_type_id: int = None) -> list[GuardianPermission]:
    queryset = await crud.guardian_permissions.query_get_multi(
        **pagination,
        content_type_id=content_type_id,
    )
    return await queryset


async def get_list_group(pagination: dict) -> list[GuardianAccessGroup]:
    queryset = await crud.guardian_group.query_get_multi(**pagination)
    return await queryset


async def create_group(name: str, users_ids: list[int], module: Module = None):
    group = await crud.guardian_group.create_group(name=name, module=module)
    users = await crud.user.get_from_ids(users_ids)
    await crud.guardian_group.add_users(group, users)
    return group


async def edit_group(group: GuardianAccessGroup, update_data: UpdateAccessGroup):
    if update_data.name:
        group = await crud.guardian_group.update_group(group=group, name=update_data.name)
    if update_data.users_ids:
        users = await crud.user.get_from_ids(update_data.users_ids)
        await crud.guardian_group.set_group_users(group, users)
    return group


async def delete_group(group_id: int):
    await crud.guardian_group.remove(group_id)


async def get_list_user_perm(pagination: dict) -> list[GuardianUserPermission]:
    queryset = await crud.guardian_user_perm.query_get_multi(**pagination)
    queryset = await crud.guardian_user_perm.join_content_type_and_permission(queryset)
    return await queryset


async def add_user_perm(create_data: CreateUserPerm) -> GuardianUserPermission:
    content_type = await crud.guardian_content_type.get_or_raise(id=create_data.content_type_id)
    permission = await crud.guardian_permissions.get_or_raise(id=create_data.permission_id)
    user = await crud.user.get_or_raise(id=create_data.user_id)
    return await crud.guardian_user_perm.add_permission(
        object_pk=create_data.object_pk,
        content_type=content_type,
        permission=permission,
        user=user,
    )


async def get_list_group_perm(pagination: dict) -> list[GuardianGroupPermission]:
    queryset = await crud.guardian_group_perm.query_get_multi(**pagination)
    queryset = await crud.guardian_group_perm.join_content_type_and_permission(queryset)
    return await queryset


async def add_group_perm(create_data: CreateGroupPerm) -> GuardianUserPermission:
    content_type = await crud.guardian_content_type.get_or_raise(id=create_data.content_type_id)
    permission = await crud.guardian_permissions.get_or_raise(id=create_data.permission_id)
    group = await crud.guardian_group.get_or_raise(id=create_data.group_id)
    return await crud.guardian_group_perm.add_permission(
        object_pk=create_data.object_pk,
        content_type=content_type,
        permission=permission,
        group=group,
    )
