from fastapi import APIRouter, Security, Depends
from fastapi_pagination import Page

from core.db.guardian import GuardianAccessGroup
from core.dependencies import get_current_user
from core.dependencies.guardian import get_group_by_id
from core.dependencies.misc import UnitOfWorkDep, PaginateParamsDep
from core.schemas.guardian import AccessGroupResponse, ContentTypeResponse, PermissionResponse, UserPermDetailResponse, GroupPermDetailResponse, \
    AccessGroupCreate, AccessGroupUpdate, UserPermCreate, GroupPermCreate, UserPermResponse, GroupPermResponse
from core.services.guardian_service import GContentTypeService, GPermissionService, GAccessGroupService, \
    GUserPermissionService, GGroupPermissionService

router = APIRouter(dependencies=[Security(get_current_user, scopes=['core:sudo'])])


@router.get('/content_types')
async def get_content_types_endpoint(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
        module_id: int = None,
        model: str = None,
) -> Page[ContentTypeResponse]:
    return await GContentTypeService(uow).filter_and_paginate(
        module_id=module_id, model=model, params=paginate_params,
        prefetch_related=['module']
    )


@router.get('/permissions')
async def get_permissions_endpoint(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
        content_type_id: int = None
) -> Page[PermissionResponse]:
    return await GPermissionService(uow).filter_and_paginate(
        content_type_id=content_type_id,
        params=paginate_params,
    )


@router.get('/groups')
async def get_groups_endpoint(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
) -> Page[AccessGroupResponse]:
    return await GAccessGroupService(uow).filter_and_paginate(
        params=paginate_params,
    )


@router.get('/groups/single', response_model=AccessGroupResponse)
async def get_single_group_endpoint(group: GuardianAccessGroup = Depends(get_group_by_id)):
    return group


@router.post('/groups')
async def create_group_endpoint(
        uow: UnitOfWorkDep,
        access_group_in: AccessGroupCreate,
) -> AccessGroupResponse:
    return await GAccessGroupService(uow).create_with_users(
        name=access_group_in.name,
        users_ids=access_group_in.user_ids,
    )


@router.put('/groups')
async def update_group_endpoint(
        uow: UnitOfWorkDep,
        access_group_in: AccessGroupUpdate,
        group: GuardianAccessGroup = Depends(get_group_by_id)
) -> AccessGroupResponse:
    return await GAccessGroupService(uow).update(
        id=group.pk,
        schema_in=access_group_in,
    )


@router.post('/groups/users')
async def add_users_to_group(
        uow: UnitOfWorkDep,
        users_ids: list[int],
        group: GuardianAccessGroup = Depends(get_group_by_id)
) -> bool:
    """Add users to guardian access group by list of users ids"""
    await GAccessGroupService(uow).add_users(
        group=group,
        users_ids=users_ids,
    )
    return True


@router.delete('/groups/users')
async def remove_users_from_group(
        uow: UnitOfWorkDep,
        users_ids: list[int],
        group: GuardianAccessGroup = Depends(get_group_by_id)
) -> bool:
    """Remove users from guardian access group by list of users ids"""
    await GAccessGroupService(uow).remove_users(
        group=group,
        users_ids=users_ids,
    )
    return True


@router.delete('/groups')
async def delete_group_endpoint(uow: UnitOfWorkDep, group_id: int):
    await GAccessGroupService(uow).delete(id=group_id)
    return True


@router.get('/permissions/users')
async def get_users_perms_endpoint(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
) -> Page[UserPermDetailResponse]:
    return await GUserPermissionService(uow).filter_and_paginate(
        params=paginate_params,
        prefetch_related=['content_type__module', 'permission']
    )


@router.post('/permissions/users')
async def add_user_permissions_endpoint(
        uow: UnitOfWorkDep,
        user_perm_in: UserPermCreate
) -> UserPermResponse:
    return await GUserPermissionService(uow).add_user_perm(user_perm_in)


@router.get('/permissions/groups')
async def get_permissions_groups_endpoint(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
) -> Page[GroupPermDetailResponse]:
    return await GGroupPermissionService(uow).filter_and_paginate(
        params=paginate_params,
        prefetch_related=['content_type__module', 'permission']
    )


@router.post('/permissions/groups')
async def add_group_permission_endpoint(
        uow: UnitOfWorkDep,
        group_perm_in: GroupPermCreate
) -> GroupPermResponse:
    return await GGroupPermissionService(uow).add_group_perm(group_perm_in)
