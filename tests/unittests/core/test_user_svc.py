import pytest

from core.db.models import Team, User
from core.dependencies.services import get_user_service
from core.exceptions import AlreadyExists, NotFound, ValidationFailed
from core.schemas.user import UserCreate, UserUpdate
from tortoise.contrib.test import TestCase


class TestUserService(TestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()

        self.user_service = get_user_service()
        self.team = await Team.create(name="Test")
        self.user = await User.create(username="SimpleUser", team_id=self.team.pk, hashed_password="...")

    async def asyncTearDown(self) -> None:
        try:
            await super().asyncTearDown()
        except Exception:
            # skip error if transaction already finalized
            # raised when using atomic transaction in 'with pytest.raises(...)'
            pass


    async def test_create_with_pass(self):
        username = 'Piter'
        password = 'superpass'
        position = 'Head'
        user_in = UserCreate(
            username=username,
            password=password,
            team_id=self.team.pk,
            position=position
        )

        created_user = await self.user_service.create_with_pass(user_in=user_in)
        assert created_user is not None

        # test success created user
        user = await self.user_service.get(username=username)
        assert user is not None
        assert user.username == username
        assert user.team_id == self.team.pk
        assert user.position == position

        # test create when user already exists
        with pytest.raises(AlreadyExists):
            await self.user_service.create_with_pass(user_in=user_in)

        # test create user with incorrect team
        user_in = UserCreate(
            username=username,
            password=password,
            team_id=0,
            position=position
        )
        with pytest.raises(NotFound):
            await self.user_service.create_with_pass(user_in=user_in)

    async def test_update_user(self):
        updated_user = await self.user_service.update_user(
            id=self.user.pk,
            schema_in=UserUpdate(username="Parker")
        )
        assert updated_user.username == "Parker"

    async def test_update_user_data(self):
        user_data = await self.user_service.update_user_data(
            id=self.user.pk,
            old_user_data=self.user.user_data,
            new_user_data={'test_field': 'test_value'},
        )
        assert user_data == {'test_field': 'test_value'}

    async def test_update_with_password(self):
        updated_user = await self.user_service.update_with_password(
            user=self.user,
            schema_in=UserUpdate(
                username="Piter Parker",
                password='superpass',
            )
        )
        assert updated_user.username == "Piter Parker"
        assert updated_user.hashed_password != '...'

    async def test_update_users_team(self):
        new_team = await Team.create(name='TestTeam2')
        await self.user_service.update_users_team(
            users_ids=[self.user.pk],
            team_id=new_team.pk,
        )
        user = await self.user_service.get(id=self.user.pk)
        assert user.team_id == new_team.pk

    async def test_delete(self):
        await self.user_service.delete(id=self.user.pk)
        is_user_exists = await self.user_service.exists(id=self.user.pk)
        assert is_user_exists is False