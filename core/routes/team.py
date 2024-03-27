from typing import Optional

from fastapi import Depends, APIRouter, Security, Response, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate
from tortoise.transactions import in_transaction

from core.db.models import Team, Variable
from core import crud

from core.dependencies import get_team_by_id, get_current_user
from core.dependencies.misc import UnitOfWorkDep
from core.schemas.team import TeamResponse, TeamListResponse, TeamCreate, TeamUpdate
from core.services.team_service import TeamService

router = APIRouter()


@router.get(
    '',
    dependencies=[Depends(get_current_user)]
)
async def get_teams(uow: UnitOfWorkDep) -> Page[TeamListResponse]:
    return await TeamService(uow).filter_and_paginate(prefetch_related=['users'])


@router.get(
    '/get',
    dependencies=[Depends(get_current_user)],
    response_model=TeamResponse
)
async def get_team(uow: UnitOfWorkDep, team: Team = Depends(get_team_by_id)):
    team_with_related = await TeamService(uow).get(id=team.pk, prefetch_related=['users', 'settings'])
    team_with_related.permissions = await TeamService(uow).get_permissions(team_with_related)
    return team_with_related


@router.post(
    '/add',
    response_model=TeamResponse,
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])]
)
async def create_team(uow: UnitOfWorkDep, team_in: TeamCreate):
    new_team = await TeamService(uow).create_with_perms_users_vars(team_in)
    team_with_related = await TeamService(uow).get(id=new_team.pk, prefetch_related=['users', 'settings'])
    return team_with_related


@router.put(
    '/edit',
    response_model=TeamResponse,
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])]
)
async def edit_team(uow: UnitOfWorkDep, team_in: TeamUpdate, team: Team = Depends(get_team_by_id)):
    team_with_related = await TeamService(uow).get(
        id=team.pk, prefetch_related=['users'])

    await TeamService(uow).update_with_perms_and_users(team=team_with_related, team_in=team_in)

    updated_team_with_related = await TeamService(uow).get(
        id=team_with_related.pk, prefetch_related=['users', 'settings'])
    return updated_team_with_related


@router.delete(
    '/remove',
    response_model=bool,
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])]
)
async def delete_team(uow: UnitOfWorkDep, team: Team = Depends(get_team_by_id)):
    await TeamService(uow).delete(id=team.pk)
    return Response(status_code=204)


@router.put(
    '/edit/users',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])]
)
async def set_team_users(
        uow: UnitOfWorkDep,
        users_ids: list[int],
        team: Team = Depends(get_team_by_id)
) -> TeamResponse:
    team_with_related = await TeamService(uow).get(
        id=team.pk, prefetch_related=['users'])
    await TeamService(uow).set_users(team=team_with_related, users_ids=users_ids)

    updated_team_with_related = await TeamService(uow).get(
        id=team.pk, prefetch_related=['users', 'settings'])
    return updated_team_with_related
