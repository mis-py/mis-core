from core.db.models import Team, User
from core.crud.base import CRUDBase


class CRUDTeam(CRUDBase):

    async def get(self, id: int) -> Team | None:
        return await self.model.get_or_none(id=id).prefetch_related("users")

    async def clear_team_users(self, team: Team):
        async for user in team.users.all():
            user.team = None
            await user.save()

    async def set_team_users(self, team: Team, users_ids: list[int]):
        for user in await User.filter(id__in=users_ids):
            user.team = team
            await user.save()

    async def create_by_name(self, name):
        return await self.model.create(name=name)


team = CRUDTeam(Team)
