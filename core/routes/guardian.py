from fastapi import APIRouter, Security, Depends

from core.db.guardian import GuardianAccessGroup
from core.dependencies import get_current_user
from core.dependencies.guardian import get_group_by_id
from core.dependencies.misc import UnitOfWorkDep, PaginateParamsDep
from core.schemas.guardian import AccessGroupResponse, ContentTypeResponse, PermissionResponse, \
    UserPermDetailResponse, GroupPermDetailResponse, AccessGroupCreate, AccessGroupUpdate, \
    UserPermCreate, GroupPermCreate, UserPermResponse, GroupPermResponse
from core.services.guardian_service import GContentTypeService, GPermissionService, GAccessGroupService, \
    GUserPermissionService, GGroupPermissionService
from core.utils.schema import MisResponse, PageResponse

router = APIRouter(dependencies=[Security(get_current_user, scopes=['core:sudo'])])


@router.get(
    '/content_types',
    response_model=PageResponse[ContentTypeResponse]
)
async def get_content_types_endpoint(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
        module_id: int = None,
        model: str = None,
):
    return await GContentTypeService(uow).filter_and_paginate(
        module_id=module_id, model=model, params=paginate_params,
        prefetch_related=['module']
    )


@router.get(
    '/permissions',
    response_model=PageResponse[PermissionResponse]
)
async def get_permissions_endpoint(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
        content_type_id: int = None
):
    return await GPermissionService(uow).filter_and_paginate(
        content_type_id=content_type_id,
        params=paginate_params,
    )


@router.get(
    '/groups',
    response_model=PageResponse[AccessGroupResponse]
)
async def get_groups_endpoint(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
):
    return await GAccessGroupService(uow).filter_and_paginate(
        params=paginate_params,
    )


@router.get(
    '/groups/single',
    response_model=MisResponse[AccessGroupResponse]
)
async def get_single_group_endpoint(group: GuardianAccessGroup = Depends(get_group_by_id)):
    return MisResponse[AccessGroupResponse](result=group)


@router.post(
    '/groups',
    response_model=MisResponse[AccessGroupResponse]
)
async def create_group_endpoint(
        uow: UnitOfWorkDep,
        access_group_in: AccessGroupCreate,
):
    result = await GAccessGroupService(uow).create_with_users(
        name=access_group_in.name,
        users_ids=access_group_in.user_ids,
    )
    return MisResponse[AccessGroupResponse](result=result)


@router.put(
    '/groups',
    response_model=MisResponse[AccessGroupResponse]
)
async def update_group_endpoint(
        uow: UnitOfWorkDep,
        access_group_in: AccessGroupUpdate,
        group: GuardianAccessGroup = Depends(get_group_by_id)
):
    result = await GAccessGroupService(uow).update(
        id=group.pk,
        schema_in=access_group_in,
    )
    return MisResponse[AccessGroupResponse](result=result)


@router.post(
    '/groups/users',
    response_model=MisResponse
)
async def add_users_to_group(
        uow: UnitOfWorkDep,
        users_ids: list[int],
        group: GuardianAccessGroup = Depends(get_group_by_id)
):
    """Add users to guardian access group by list of users ids"""
    await GAccessGroupService(uow).add_users(
        group=group,
        users_ids=users_ids,
    )
    return MisResponse()


@router.delete(
    '/groups/users',
    response_model=MisResponse
)
async def remove_users_from_group(
        uow: UnitOfWorkDep,
        users_ids: list[int],
        group: GuardianAccessGroup = Depends(get_group_by_id)
):
    """Remove users from guardian access group by list of users ids"""
    await GAccessGroupService(uow).remove_users(
        group=group,
        users_ids=users_ids,
    )
    return MisResponse()


@router.delete(
    '/groups',
    response_model=MisResponse
)
async def delete_group_endpoint(uow: UnitOfWorkDep, group_id: int):
    await GAccessGroupService(uow).delete(id=group_id)
    return MisResponse()


@router.get(
    '/permissions/users',
    response_model=PageResponse[UserPermDetailResponse]
)
async def get_users_perms_endpoint(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
):
    return await GUserPermissionService(uow).filter_and_paginate(
        params=paginate_params,
        prefetch_related=['content_type__module', 'permission']
    )


@router.post(
    '/permissions/users',
    response_model=MisResponse[UserPermResponse]
)
async def add_user_permissions_endpoint(
        uow: UnitOfWorkDep,
        user_perm_in: UserPermCreate
):
    result = await GUserPermissionService(uow).add_user_perm(user_perm_in)
    return MisResponse[UserPermResponse](result=result)


@router.get(
    '/permissions/groups',
    response_model=PageResponse[GroupPermDetailResponse]
)
async def get_permissions_groups_endpoint(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
):
    return await GGroupPermissionService(uow).filter_and_paginate(
        params=paginate_params,
        prefetch_related=['content_type__module', 'permission']
    )


@router.post(
    '/permissions/groups',
    response_model=MisResponse[GroupPermResponse]
)
async def add_group_permission_endpoint(
        uow: UnitOfWorkDep,
        group_perm_in: GroupPermCreate
):
    result = await GGroupPermissionService(uow).add_group_perm(group_perm_in)
    return MisResponse[GroupPermResponse](result=result)
