from fastapi import Depends, APIRouter, Security, Response

from core.db.models import Team, Variable
from core import crud

from core.dependencies import get_team_by_id, get_current_user
from core.dependencies.path import PaginationDep
from core.schemas.team import TeamData, TeamListModel, TeamDetailModel

router = APIRouter()


@router.get(
    '',
    response_model=list[TeamListModel],
    dependencies=[Depends(get_current_user)]
)
async def get_teams(pagination: PaginationDep):
    query = await crud.team.query_get_multi(**pagination)
    return await TeamListModel.from_queryset(query)


@router.get(
    '/get',
    dependencies=[Depends(get_current_user)],
    response_model=list[TeamDetailModel]
)
async def get_team(team: Team = Depends(get_team_by_id)):
    schema = await TeamDetailModel.from_tortoise_orm(team)
    schema.permissions = await team.get_granted_permissions(scopes_list=True)
    return schema


@router.post(
    '/add',
    response_model=TeamDetailModel,
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])]
)
async def create_team(team_data: TeamData):
    new_team = await crud.team.create_by_name(name=team_data.name)

    if team_data.permissions:
        await new_team.set_permissions(team_data.permissions)

    if team_data.users_ids:
        await crud.team.set_team_users(team=new_team, users_ids=team_data.users_ids)

    for variable in team_data.settings:
        await crud.variable_value.set_variable_value(
            await Variable.get(id=variable.setting_id),
            variable.new_value, team=new_team
        )
    return await TeamDetailModel.from_tortoise_orm(new_team)


@router.put(
    '/edit',
    response_model=TeamDetailModel,
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])]
)
async def edit_team(team_data: TeamData, team: Team = Depends(get_team_by_id)):
    if team_data.name:
        await crud.team.update(team, {"name": team_data.name})

    if team_data.users_ids:
        await crud.team.clear_team_users(team)  # clear old team members
        await crud.team.set_team_users(team, team_data.users_ids)  # set new team members

    if team_data.permissions:
        await team.set_permissions(team_data.permissions)

    return await TeamDetailModel.from_tortoise_orm(team)


@router.delete(
    '/remove',
    response_model=bool,
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])]
)
async def delete_team(team: Team = Depends(get_team_by_id)):
    await crud.team.remove(id=team.id)
    return Response(status_code=204)


@router.put(
    '/edit/users',
    response_model=bool,
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:teams'])]
)
async def set_team_users(users_ids: list[int], team: Team = Depends(get_team_by_id)):
    await crud.team.clear_team_users(team)  # clear old team members
    await crud.team.set_team_users(team, users_ids)  # set new team members
    return Response(status_code=200)
