from core.db.models import Team
from core.exceptions import ValidationFailed, MISError
from core.schemas.team import TeamCreate, TeamUpdate
from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork
from services.variables.utils import type_convert


class TeamService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.team_repo)
        self.uow = uow

    async def create_with_perms_users_vars(self, team_in: TeamCreate):
        async with self.uow:
            new_team = await self.uow.team_repo.create(data={'name': team_in.name})

            if team_in.permissions:
                await new_team.set_permissions(team_in.permissions)

            if team_in.users_ids:
                await self.uow.user_repo.update_list(update_ids=team_in.users_ids, data={'team_id': new_team.id})

            for setting in team_in.variables:
                variable = await self.uow.variable_repo.get(id=setting.setting_id)
                try:
                    type_convert(value=setting.new_value, to_type=variable.type)
                except ValueError:
                    raise ValidationFailed(
                        f"Can't set setting {variable.key}. Value is not '{variable.type}' type",
                    )

                if variable.is_global:
                    raise ValidationFailed(
                        f"Can't set global setting {variable.key} as local setting for user",
                    )

                await self.uow.variable_value_repo.update_or_create(
                    variable_id=variable.pk,
                    value=setting.new_value,
                    team_id=new_team.pk,
                )
        return new_team

    async def update_with_perms_and_users(self, team: Team, team_in: TeamUpdate):
        async with self.uow:
            if team_in.name:
                team.name = team_in.name
                await self.uow.team_repo.save(obj=team)

            if team_in.permissions:
                await team.set_permissions(team_in.permissions)

            if team_in.users_ids:
                await self.set_users(team=team, users_ids=team_in.users_ids)
        return team

    async def get_permissions(self, team: Team):
        return await team.get_granted_permissions(scopes_list=True)

    async def set_users(self, team: Team, users_ids: list[int]):
        old_team_users_ids = [user.pk for user in team.users]
        await self.uow.user_repo.update_list(
            update_ids=old_team_users_ids,
            data={'team_id': None})  # clear old team members
        await self.uow.user_repo.update_list(
            update_ids=users_ids,
            data={'team_id': team.pk})  # set new team members

    async def delete(self, **filters) -> None:
        if 'id' in filters and filters['id'] == 1:
            raise MISError("Team with id '1' can't be deleted.")
        await self.repo.delete(**filters)
