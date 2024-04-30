from fastapi import APIRouter, Depends, Security, Query

from core.db.models import User, Team
from core.dependencies.misc import UnitOfWorkDep
from core.exceptions import MISError
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


# TODO remove here pagination
@router.get(
    '/granted/my',
    response_model=PageResponse[GrantedPermissionResponse]
)
async def get_my_granted_permissions(uow: UnitOfWorkDep, user: User = Depends(get_current_user)):
    return await GrantedPermissionService(uow).filter_and_paginate(
        user_id=user.pk,
        prefetch_related=['team', 'user', 'permission__app'],
    )


# TODO remove here pagination
@router.get(
    '/granted',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])],
    response_model=PageResponse[GrantedPermissionResponse],
)
async def get_granted_permissions(
        uow: UnitOfWorkDep,
        user_id: int = Query(default=None),
        team_id: int = Query(default=None)
):
    if sum(1 for x in [team_id, user_id] if x) != 1:
        raise MISError("Use only one filter")

    if user_id is not None:
        user = await get_user_by_id(user_id)

        return await GrantedPermissionService(uow).filter_and_paginate(
            user_id=user.pk,
            prefetch_related=['team', 'user', 'permission__app'],
        )

    if team_id is not None:
        team = await get_team_by_id(team_id)

        return await GrantedPermissionService(uow).filter_and_paginate(
            team_id=team.pk,
            prefetch_related=['team', 'user', 'permission__app'],
        )


@router.put(
    '/granted',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])],
    response_model=MisResponse,
)
async def set_granted_permissions(
        uow: UnitOfWorkDep,
        permissions: list[PermissionUpdate],
        user_id: int = Query(default=None),
        team_id: int = Query(default=None)
):
    if sum(1 for x in [team_id, user_id] if x) != 1:
        raise MISError("Use only one filter")

    if user_id is not None:
        user = await get_user_by_id(user_id)
        await GrantedPermissionService(uow).set_for_user(permissions=permissions, user=user)

    if team_id is not None:
        team = await get_team_by_id(team_id)
        await GrantedPermissionService(uow).set_for_team(permissions=permissions, team=team)

    return MisResponse()

