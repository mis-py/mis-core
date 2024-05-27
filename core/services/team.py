from tortoise import transactions

from core.db.models import Team
from core.exceptions import ValidationFailed, MISError
from core.repositories.team import ITeamRepository
from core.repositories.user import IUserRepository
from core.repositories.variable import IVariableRepository
from core.repositories.variable_value import IVariableValueRepository
from core.schemas.team import TeamCreate, TeamUpdate
from core.services.base.base_service import BaseService
from libs.variables.utils import type_convert


class TeamService(BaseService):
    def __init__(
            self,
            team_repo: ITeamRepository,
            user_repo: IUserRepository,
            variable_repo: IVariableRepository,
            variable_value_repo: IVariableValueRepository,
    ):
        self.team_repo = team_repo
        self.user_repo = user_repo
        self.variable_repo = variable_repo
        self.variable_value_repo = variable_value_repo
        super().__init__(repo=team_repo)

    @transactions.atomic()
    async def create_with_perms_users_vars(self, team_in: TeamCreate):
        new_team = await self.team_repo.create(data={'name': team_in.name})

        if team_in.permissions:
            await new_team.set_permissions(team_in.permissions)

        if team_in.users_ids:
            await self.user_repo.update_list(update_ids=team_in.users_ids, data={'team_id': new_team.id})

        for variable_in in team_in.variables:
            variable = await self.uow.variable_repo.get(id=variable_in.variable_id)
            try:
                type_convert(value=variable_in.new_value, to_type=variable.type)
            except ValueError:
                raise ValidationFailed(
                    f"Can't set setting {variable.key}. Value is not '{variable.type}' type",
                )

            if variable.is_global:
                raise ValidationFailed(
                    f"Can't set global setting {variable.key} as local setting for user",
                )

            await self.variable_value_repo.update_or_create(
                variable_id=variable.pk,
                value=variable_in.new_value,
                team_id=new_team.pk,
            )
        return new_team

    @transactions.atomic()
    async def update_with_perms_and_users(self, team: Team, team_in: TeamUpdate):
        if team_in.name:
            team.name = team_in.name
            await self.team_repo.save(obj=team)

        if team_in.permissions:
            await team.set_permissions(team_in.permissions)

        if team_in.users_ids:
            await self.set_users(team=team, users_ids=team_in.users_ids)
        return team

    async def get_permissions(self, team: Team):
        return await team.get_granted_permissions(scopes_list=True)

    async def set_users(self, team: Team, users_ids: list[int]):
        old_team_users_ids = [user.pk for user in team.users]
        await self.user_repo.update_list(
            update_ids=old_team_users_ids,
            data={'team_id': None})  # clear old team members
        await self.user_repo.update_list(
            update_ids=users_ids,
            data={'team_id': team.pk})  # set new team members

    async def delete(self, **filters) -> None:
        if 'id' in filters and filters['id'] == 1:
            raise MISError("Team with id '1' can't be deleted")
        await self.repo.delete(**filters)
