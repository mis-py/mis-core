from fastapi import Depends, APIRouter, Security

from core.db.models import Team

from core.dependencies.path import get_team_by_id
from core.dependencies.security import get_current_user
from core.dependencies.uow import UnitOfWorkDep
from core.schemas.team import TeamResponse, TeamListResponse, TeamCreate, TeamUpdate
from core.utils.schema import PageResponse, MisResponse
from core.services.team import TeamService

router = APIRouter()


@router.get(
    '',
    dependencies=[Depends(get_current_user)],
    response_model=PageResponse[TeamListResponse],
)
async def get_teams(uow: UnitOfWorkDep):
    return await TeamService(uow).filter_and_paginate(prefetch_related=['users'])


@router.get(
    '/get',
    dependencies=[Depends(get_current_user)],
    response_model=MisResponse[TeamResponse]
)
async def get_team(uow: UnitOfWorkDep, team: Team = Depends(get_team_by_id)):
    team_with_related = await TeamService(uow).get(id=team.pk, prefetch_related=['users', 'variable_values'])
    team_with_related.permissions = await TeamService(uow).get_permissions(team_with_related)

    return MisResponse[TeamResponse](result=team_with_related)


@router.post(
    '/add',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])],
    response_model=MisResponse[TeamResponse],
)
async def create_team(uow: UnitOfWorkDep, team_in: TeamCreate):
    new_team = await TeamService(uow).create_with_perms_users_vars(team_in)
    team_with_related = await TeamService(uow).get(id=new_team.pk, prefetch_related=['users', 'variable_values'])

    return MisResponse[TeamResponse](result=team_with_related)


@router.put(
    '/edit',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])],
    response_model=MisResponse[TeamResponse],
)
async def edit_team(uow: UnitOfWorkDep, team_in: TeamUpdate, team: Team = Depends(get_team_by_id)):
    team_with_related = await TeamService(uow).get(
        id=team.pk, prefetch_related=['users'])

    await TeamService(uow).update_with_perms_and_users(team=team_with_related, team_in=team_in)

    updated_team_with_related = await TeamService(uow).get(
        id=team_with_related.pk, prefetch_related=['users', 'variable_values'])

    return MisResponse[TeamResponse](result=updated_team_with_related)


@router.delete(
    '/remove',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])],
    response_model=MisResponse
)
async def delete_team(uow: UnitOfWorkDep, team: Team = Depends(get_team_by_id)):
    await TeamService(uow).delete(id=team.pk)

    return MisResponse()


@router.put(
    '/edit/users',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])],
    response_model=MisResponse[TeamResponse]
)
async def set_team_users(
        uow: UnitOfWorkDep,
        users_ids: list[int],
        team: Team = Depends(get_team_by_id)
):
    team_with_related = await TeamService(uow).get(
        id=team.pk, prefetch_related=['users'])
    await TeamService(uow).set_users(team=team_with_related, users_ids=users_ids)

    updated_team_with_related = await TeamService(uow).get(
        id=team.pk, prefetch_related=['users', 'variable_values'])
    return MisResponse[TeamResponse](result=updated_team_with_related)
