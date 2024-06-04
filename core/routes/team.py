from typing import Annotated

from fastapi import Depends, APIRouter, Security

from core.db.models import Team

from core.dependencies.path import get_team_by_id
from core.dependencies.security import get_current_user
from core.dependencies.services import get_team_service
from core.schemas.team import TeamResponse, TeamListResponse, TeamCreate, TeamUpdate
from core.utils.schema import PageResponse, MisResponse
from core.services.team import TeamService

router = APIRouter()


@router.get(
    '',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])],
    response_model=PageResponse[TeamListResponse],
)
async def get_teams(
        team_service: Annotated[TeamService, Depends(get_team_service)]
):
    return await team_service.filter_and_paginate(prefetch_related=['users'])


@router.get(
    '/get',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])],
    response_model=MisResponse[TeamResponse]
)

async def get_team(
        team_service: Annotated[TeamService, Depends(get_team_service)],
        team: Team = Depends(get_team_by_id)
):
    team_with_related = await team_service.get(id=team.pk, prefetch_related=['users', 'variable_values'])
    team_with_related.permissions = await team_service.get_permissions(team_with_related)

    return MisResponse[TeamResponse](result=team_with_related)


@router.post(
    '/add',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])],
    response_model=MisResponse[TeamResponse],
)

async def create_team(
        team_service: Annotated[TeamService, Depends(get_team_service)],
        team_in: TeamCreate,
):
    new_team = await team_service.create_with_perms_users_vars(team_in)
    team_with_related = await team_service.get(id=new_team.pk, prefetch_related=['users', 'variable_values'])

    return MisResponse[TeamResponse](result=team_with_related)


@router.put(
    '/edit',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])],
    response_model=MisResponse[TeamResponse],
)
async def edit_team(
        team_service: Annotated[TeamService, Depends(get_team_service)],
        team_in: TeamUpdate,
        team: Team = Depends(get_team_by_id)):
    team_with_related = await team_service.get(id=team.pk, prefetch_related=['users'])

    await team_service.update_with_perms_and_users(team=team_with_related, team_in=team_in)

    updated_team_with_related = await team_service.get(
        id=team_with_related.pk, prefetch_related=['users', 'variable_values'])

    return MisResponse[TeamResponse](result=updated_team_with_related)


@router.delete(
    '/remove',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])],
    response_model=MisResponse
)
async def delete_team(
        team_service: Annotated[TeamService, Depends(get_team_service)],
        team: Team = Depends(get_team_by_id)
):
    await team_service.delete(id=team.pk)

    return MisResponse()


@router.put(
    '/edit/users',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])],
    response_model=MisResponse[TeamResponse]
)
async def set_team_users(
        team_service: Annotated[TeamService, Depends(get_team_service)],
        users_ids: list[int],
        team: Team = Depends(get_team_by_id)
):
    team_with_related = await team_service.get(
        id=team.pk, prefetch_related=['users'])
    await team_service.set_users(team=team_with_related, users_ids=users_ids)

    updated_team_with_related = await team_service.get(
        id=team.pk, prefetch_related=['users', 'variable_values'])
    return MisResponse[TeamResponse](result=updated_team_with_related)
