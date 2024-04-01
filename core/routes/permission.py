from fastapi import APIRouter, Depends, Security
from fastapi_pagination import Page

from core.db.models import User, Team
from core.dependencies.misc import UnitOfWorkDep
from core.schemas.permission import GrantedPermissionResponse, PermissionResponse, PermissionUpdate
from core.dependencies import get_user_by_id, get_team_by_id, get_current_user
from core.services.granted_permission import GrantedPermissionService
from core.services.permission import PermissionService

router = APIRouter()


@router.get(
    '',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])],
    response_model=Page[PermissionResponse]
)
async def permissions_list(uow: UnitOfWorkDep):
    return await PermissionService(uow).filter_and_paginate(
        prefetch_related=['app'],
    )


@router.get(
    '/my',
    response_model=Page[GrantedPermissionResponse]
)
async def get_my_permissions(uow: UnitOfWorkDep, user: User = Depends(get_current_user)):
    return await GrantedPermissionService(uow).filter_and_paginate(
        user_id=user.pk,
        prefetch_related=['team', 'user', 'permission__app'],
    )


@router.get(
    '/get/user',
    response_model=Page[GrantedPermissionResponse],
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])]
)
async def get_user_permissions(uow: UnitOfWorkDep, user: User = Depends(get_user_by_id)):
    return await GrantedPermissionService(uow).filter_and_paginate(
        user_id=user.pk,
        prefetch_related=['team', 'user', 'permission__app'],
    )

@router.put(
    '/edit/user',
    response_model=Page[GrantedPermissionResponse],
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])]
)
async def set_user_permissions(
        uow: UnitOfWorkDep,
        permissions: list[PermissionUpdate],
        user: User = Depends(get_user_by_id)
):
    await GrantedPermissionService(uow).set_for_user(permissions=permissions, user=user)
    return await GrantedPermissionService(uow).filter_and_paginate(
        user_id=user.pk,
        prefetch_related=['team', 'user', 'permission__app']
    )


@router.get(
    '/get/team',
    response_model=Page[GrantedPermissionResponse],
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])]
)
async def get_team_permissions(uow: UnitOfWorkDep, team: Team = Depends(get_team_by_id)):
    return await GrantedPermissionService(uow).filter_and_paginate(
        team_id=team.pk,
        prefetch_related=['team', 'user', 'permission__app'],
    )


@router.put(
    '/edit/team',
    response_model=list[GrantedPermissionResponse],
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])]
)
async def set_team_permissions(
        uow: UnitOfWorkDep,
        permissions: Page[PermissionUpdate],
        team: Team = Depends(get_team_by_id)
):
    await GrantedPermissionService(uow).set_for_team(permissions=permissions, team=team)
    return await GrantedPermissionService(uow).filter_and_paginate(
        team_id=team.pk,
        prefetch_related=['team', 'user', 'permission']
    )
