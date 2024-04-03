from fastapi import APIRouter, Depends, Security, Response
from fastapi_pagination import Page

from core.db.models import User, Team
from core.dependencies.misc import UnitOfWorkDep
from core.schemas.permission import GrantedPermissionResponse, PermissionResponse, PermissionUpdate
from core.dependencies import get_user_by_id, get_team_by_id, get_current_user
from core.services.granted_permission import GrantedPermissionService
from core.services.permission import PermissionService
from core.utils.schema import PageResponse, MisResponse

router = APIRouter()


@router.get(
    '',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])],
    response_model=PageResponse[PermissionResponse]
)
async def permissions_list(uow: UnitOfWorkDep):
    return await PermissionService(uow).filter_and_paginate(
        prefetch_related=['app'],
    )


@router.get(
    '/my',
    response_model=PageResponse[GrantedPermissionResponse]
)
async def get_my_permissions(uow: UnitOfWorkDep, user: User = Depends(get_current_user)):
    return await GrantedPermissionService(uow).filter_and_paginate(
        user_id=user.pk,
        prefetch_related=['team', 'user', 'permission__app'],
    )


@router.get(
    '/get/user',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])],
    response_model=PageResponse[GrantedPermissionResponse],
)
async def get_user_permissions(uow: UnitOfWorkDep, user: User = Depends(get_user_by_id)):
    return await GrantedPermissionService(uow).filter_and_paginate(
        user_id=user.pk,
        prefetch_related=['team', 'user', 'permission__app'],
    )


@router.put(
    '/edit/user',

    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])],
    response_model=MisResponse[GrantedPermissionResponse],
)
async def set_user_permissions(
        uow: UnitOfWorkDep,
        permissions: list[PermissionUpdate],
        user: User = Depends(get_user_by_id)
):
    await GrantedPermissionService(uow).set_for_user(permissions=permissions, user=user)

    filtered_permissions = await GrantedPermissionService(uow).filter(
        user_id=user.pk,
        prefetch_related=['team', 'user', 'permission__app']
    )

    return MisResponse[GrantedPermissionResponse](result=filtered_permissions)


@router.get(
    '/get/team',
    response_model=PageResponse[GrantedPermissionResponse],
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])]
)
async def get_team_permissions(uow: UnitOfWorkDep, team: Team = Depends(get_team_by_id)):
    return await GrantedPermissionService(uow).filter_and_paginate(
        team_id=team.pk,
        prefetch_related=['team', 'user', 'permission__app'],
    )


@router.put(
    '/edit/team',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])],
    response_model=MisResponse[list[GrantedPermissionResponse]]
)
async def set_team_permissions(
        uow: UnitOfWorkDep,
        permissions: list[PermissionUpdate],
        team: Team = Depends(get_team_by_id)
):
    await GrantedPermissionService(uow).set_for_team(permissions=permissions, team=team)

    filtered_permissions = await GrantedPermissionService(uow).filter(
        team_id=team.pk,
        prefetch_related=['team', 'user', 'permission']
    )

    return MisResponse[list[GrantedPermissionResponse]](result=filtered_permissions)
