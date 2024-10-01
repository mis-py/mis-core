from tortoise.contrib.test import TestCase

from core.db.models import User, Team
from core.dependencies.services import get_team_service
from core.schemas.team import TeamCreate, TeamUpdate


class TestTeamService(TestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.team_service = get_team_service()
        self.team = await Team.create(name='Setup team')
        self.user = await User.create(username='Test', team_id=self.team.pk, hashed_password='...')

    async def test_create_with_perms_users_vars(self):
        team_name = 'Test for create'
        team_in = TeamCreate(
            name=team_name,
            users_ids=[self.user.pk],
        )
        team = await self.team_service.create_with_perms_users_vars(
            team_in=team_in,
        )
        await team.fetch_related('users', 'variable_values')
        assert team.name == team_name
        assert self.user.pk in [user.pk for user in team.users]

    async def test_set_users(self):
        created_team = await Team.create(name='Team for set users')
        await created_team.fetch_related('users')

        await self.team_service.set_users(created_team, users_ids=[self.user.pk])

        team = await self.team_service.get(id=created_team.pk, prefetch_related=['users'])
        assert self.user.pk in [user.pk for user in team.users]

    async def test_update_with_perms_and_users(self):
        await self.team.fetch_related('users')

        team_in = TeamUpdate(
            name='Updated Team',
            users_ids=[self.user.pk],
        )
        updated_team = await self.team_service.update_with_perms_and_users(
            team=self.team,
            team_in=team_in,
        )
        await updated_team.fetch_related('users')

        assert updated_team.name == 'Updated Team'
        assert self.user.pk in [user.pk for user in updated_team.users]

    async def test_delete(self):
        team = await Team.create(name='Team for delete')
        await self.team_service.delete(id=team.pk)
        is_team_exists = await self.team_service.exists(id=self.user.pk)
        assert is_team_exists is False
