from typing import Annotated

from fastapi import APIRouter, Depends, Security, Query

from core.db.models import User, Team
from core.dependencies.services import get_permission_service, get_granted_permission_service, get_user_service, \
    get_team_service
from core.exceptions import MISError
from core.schemas.permission import GrantedPermissionResponse, PermissionResponse, PermissionUpdate
from core.dependencies.path import get_user_by_id, get_team_by_id
from core.dependencies.security import get_current_user
from core.services.granted_permission import GrantedPermissionService
from core.services.permission import PermissionService
from core.services.team import TeamService
from core.services.user import UserService
from core.utils.schema import PageResponse, MisResponse

router = APIRouter()


@router.get(
    '',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])],
    response_model=PageResponse[PermissionResponse]
)
async def permissions_list(
        permission_service: Annotated[PermissionService, Depends(get_permission_service)]
):
    return await permission_service.filter_and_paginate(
        prefetch_related=['app'],
    )


@router.get(
    '/granted/my',
    response_model=MisResponse[list[GrantedPermissionResponse]]
)
async def get_my_granted_permissions(
        granted_permission_service: Annotated[GrantedPermissionService, Depends(get_granted_permission_service)],
        user: User = Depends(get_current_user)
):
    granted_permissions = await granted_permission_service.filter(
        user_id=user.pk,
        prefetch_related=['team', 'user', 'permission__app'],
    )
    return MisResponse[list[GrantedPermissionResponse]](result=granted_permissions)


@router.get(
    '/granted',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])],
    response_model=MisResponse[list[GrantedPermissionResponse]],
)
async def get_granted_permissions(
        granted_permission_service: Annotated[GrantedPermissionService, Depends(get_granted_permission_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        team_service: Annotated[TeamService, Depends(get_team_service)],
        user_id: int = Query(default=None),
        team_id: int = Query(default=None)
):
    if sum(1 for x in [team_id, user_id] if x) != 1:
        raise MISError("Use only one filter")

    if user_id is not None:
        user = await user_service.get_or_raise(id=user_id)

        granted_permissions = await granted_permission_service.filter(
            user_id=user.pk,
            # TODO create example with nested prefetch
            prefetch_related=['team', 'user', 'permission__app'],
        )

        return MisResponse[list[GrantedPermissionResponse]](result=granted_permissions)

    if team_id is not None:
        team = await team_service.get_or_raise(id=team_id)

        granted_permissions = await granted_permission_service.filter(
            team_id=team.pk,
            prefetch_related=['team', 'user', 'permission__app'],
        )

        return MisResponse[list[GrantedPermissionResponse]](result=granted_permissions)


@router.put(
    '/granted',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])],
    response_model=MisResponse,
)
async def set_granted_permissions(
        granted_permission_service: Annotated[GrantedPermissionService, Depends(get_granted_permission_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        team_service: Annotated[TeamService, Depends(get_team_service)],
        permissions: list[PermissionUpdate],
        user_id: int = Query(default=None),
        team_id: int = Query(default=None)
):
    if sum(1 for x in [team_id, user_id] if x) != 1:
        raise MISError("Use only one filter")

    if user_id is not None:
        user = await user_service.get_or_raise(id=user_id)
        await granted_permission_service.set_for_user(permissions=permissions, user=user)

    if team_id is not None:
        team = await team_service.get_or_raise(id=team_id)
        await granted_permission_service.set_for_team(permissions=permissions, team=team)

    return MisResponse()
