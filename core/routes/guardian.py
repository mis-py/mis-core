from fastapi import APIRouter, Security, Depends

from core.db.guardian import GuardianAccessGroup
from core.dependencies import get_current_user
from core.dependencies.guardian import get_group_by_id
from core.dependencies.path import PaginationDep
from core.schemas.guardian import ReadAccessGroup, ReadContentType, ReadPermission, ReadUserPerm, ReadGroupPerm, \
    CreateAccessGroup, UpdateAccessGroup, CreateUserPerm, CreateGroupPerm, SimpleUserPerm, SimpleGroupPerm
from core.services import guardian_service

router = APIRouter(dependencies=[Security(get_current_user, scopes=['core:sudo'])])


@router.get('/content_types', response_model=list[ReadContentType])
async def get_content_types_endpoint(pagination: PaginationDep, module_id: int = None, model: str = None):
    return await guardian_service.get_list_content_type(module_id=module_id, model=model, pagination=pagination)


@router.get('/permissions', response_model=list[ReadPermission])
async def get_permissions_endpoint(pagination: PaginationDep, content_type_id: int = None):
    return await guardian_service.get_list_permission(pagination=pagination, content_type_id=content_type_id)


@router.get('/groups', response_model=list[ReadAccessGroup])
async def get_groups_endpoint(pagination: PaginationDep):
    return await guardian_service.get_list_group(pagination=pagination)


@router.get('/groups/get', response_model=ReadAccessGroup)
async def get_group_endpoint(group: GuardianAccessGroup = Depends(get_group_by_id)):
    return group


@router.post('/groups/add', response_model=ReadAccessGroup)
async def create_group_endpoint(create_data: CreateAccessGroup):
    return await guardian_service.create_group(
        name=create_data.name,
        users_ids=create_data.users_ids,
    )


@router.put('/groups/edit', response_model=ReadAccessGroup)
async def edit_group_endpoint(update_data: UpdateAccessGroup, group: GuardianAccessGroup = Depends(get_group_by_id)):
    return await guardian_service.edit_group(group=group, update_data=update_data)


@router.delete('/groups/remove')
async def delete_group_endpoint(group_id: int):
    return await guardian_service.delete_group(group_id=group_id)


@router.get('/permissions/users', response_model=list[ReadUserPerm])
async def get_users_perms_endpoint(pagination: PaginationDep):
    return await guardian_service.get_list_user_perm(pagination=pagination)


@router.post('/permissions/users', response_model=SimpleUserPerm)
async def add_user_permissions_endpoint(user_perm_data: CreateUserPerm):
    return await guardian_service.add_user_perm(user_perm_data)


@router.get('/permissions/groups', response_model=list[ReadGroupPerm])
async def get_permissions_groups_endpoint(pagination: PaginationDep):
    return await guardian_service.get_list_group_perm(pagination=pagination)


@router.post('/permissions/groups', response_model=SimpleGroupPerm)
async def add_group_permission_endpoint(create_data: CreateGroupPerm):
    return await guardian_service.add_group_perm(create_data=create_data)
