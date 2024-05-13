from typing import Annotated

from fastapi import APIRouter, Security, Depends

from core.db.guardian import GuardianAccessGroup
from core.dependencies.security import get_current_user
from core.dependencies.path import get_group_by_id
from core.dependencies.misc import PaginateParamsDep
from core.dependencies.services import get_g_content_type_service, get_g_permission_service, get_g_access_group_service, \
    get_g_user_permission_service, get_g_group_permission_service
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
        g_content_type_service: Annotated[GContentTypeService, Depends(get_g_content_type_service)],
        paginate_params: PaginateParamsDep,
        module_id: int = None,
        model: str = None,
):
    return await g_content_type_service.filter_and_paginate(
        module_id=module_id, model=model, params=paginate_params,
        prefetch_related=['module']
    )


@router.get(
    '/permissions',
    response_model=PageResponse[PermissionResponse]
)
async def get_permissions_endpoint(
        g_permission_service: Annotated[GPermissionService, Depends(get_g_permission_service)],
        paginate_params: PaginateParamsDep,
        content_type_id: int = None
):
    return await g_permission_service.filter_and_paginate(
        content_type_id=content_type_id,
        params=paginate_params,
    )


@router.get(
    '/groups',
    response_model=PageResponse[AccessGroupResponse]
)
async def get_groups_endpoint(
        g_access_group_service: Annotated[GAccessGroupService, Depends(get_g_access_group_service)],
        paginate_params: PaginateParamsDep,
):
    return await g_access_group_service.filter_and_paginate(
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
        g_access_group_service: Annotated[GAccessGroupService, Depends(get_g_access_group_service)],
        access_group_in: AccessGroupCreate,
):
    result = await g_access_group_service.create_with_users(
        name=access_group_in.name,
        users_ids=access_group_in.user_ids,
    )
    return MisResponse[AccessGroupResponse](result=result)


@router.put(
    '/groups',
    response_model=MisResponse[AccessGroupResponse]
)
async def update_group_endpoint(
        g_access_group_service: Annotated[GAccessGroupService, Depends(get_g_access_group_service)],
        access_group_in: AccessGroupUpdate,
        group: GuardianAccessGroup = Depends(get_group_by_id)
):
    result = await g_access_group_service.update(
        id=group.pk,
        schema_in=access_group_in,
    )
    return MisResponse[AccessGroupResponse](result=result)


@router.post(
    '/groups/users',
    response_model=MisResponse
)
async def add_users_to_group(
        g_access_group_service: Annotated[GAccessGroupService, Depends(get_g_access_group_service)],
        users_ids: list[int],
        group: GuardianAccessGroup = Depends(get_group_by_id)
):
    """Add users to guardian access group by list of users ids"""
    await g_access_group_service.add_users(
        group=group,
        users_ids=users_ids,
    )
    return MisResponse()


@router.delete(
    '/groups/users',
    response_model=MisResponse
)
async def remove_users_from_group(
        g_access_group_service: Annotated[GAccessGroupService, Depends(get_g_access_group_service)],
        users_ids: list[int],
        group: GuardianAccessGroup = Depends(get_group_by_id)
):
    """Remove users from guardian access group by list of users ids"""
    await g_access_group_service.remove_users(
        group=group,
        users_ids=users_ids,
    )
    return MisResponse()


@router.delete(
    '/groups',
    response_model=MisResponse
)
async def delete_group_endpoint(
        g_access_group_service: Annotated[GAccessGroupService, Depends(get_g_access_group_service)],
        group_id: int,
):
    await g_access_group_service.delete(id=group_id)
    return MisResponse()


@router.get(
    '/permissions/users',
    response_model=PageResponse[UserPermDetailResponse]
)
async def get_users_perms_endpoint(
        g_user_permission_service: Annotated[GUserPermissionService, Depends(get_g_user_permission_service)],
        paginate_params: PaginateParamsDep,
):
    return await g_user_permission_service.filter_and_paginate(
        params=paginate_params,
        prefetch_related=['content_type__module', 'permission']
    )


@router.post(
    '/permissions/users',
    response_model=MisResponse[UserPermResponse]
)
async def add_user_permissions_endpoint(
        g_user_permission_service: Annotated[GUserPermissionService, Depends(get_g_user_permission_service)],
        user_perm_in: UserPermCreate
):
    result = await g_user_permission_service.add_user_perm(user_perm_in)
    return MisResponse[UserPermResponse](result=result)


@router.get(
    '/permissions/groups',
    response_model=PageResponse[GroupPermDetailResponse]
)
async def get_permissions_groups_endpoint(
        g_group_permission_service: Annotated[GGroupPermissionService, Depends(get_g_group_permission_service)],
        paginate_params: PaginateParamsDep,
):
    return await g_group_permission_service.filter_and_paginate(
        params=paginate_params,
        prefetch_related=['content_type__module', 'permission']
    )


@router.post(
    '/permissions/groups',
    response_model=MisResponse[GroupPermResponse]
)
async def add_group_permission_endpoint(
        g_group_permission_service: Annotated[GGroupPermissionService, Depends(get_g_group_permission_service)],
        group_perm_in: GroupPermCreate
):
    result = await g_group_permission_service.add_group_perm(group_perm_in)
    return MisResponse[GroupPermResponse](result=result)
