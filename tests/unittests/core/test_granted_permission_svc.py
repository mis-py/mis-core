from unittest.mock import Mock

from tortoise.contrib.test import TestCase

from core.db.models import Module, Team, User
from core.dependencies.services import get_granted_permission_service, get_permission_service


class TestGrantedPermissionService(TestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.granted_permission_service = get_granted_permission_service()
        self.module = await Module.create(name='test_module')
        permission_service = get_permission_service()

        self.permission = await permission_service.create_with_scope(
            name='Full access',
            scope='sudo',
            module=self.module,
        )

    async def test_set_for_user(self):
        team = await Team.create(name='Test')
        user = await User.create(username='Test', team_id=team.pk, hashed_password='...')

        # granted True
        permission_schema = Mock(permission_id=self.permission.pk, granted=True)
        await self.granted_permission_service.set_for_user(
            permissions=[permission_schema],
            user=user,
        )

        is_exists = await user.granted_permissions.filter(permission_id=self.permission.pk).exists()
        assert is_exists is True

        # granted False
        permission_schema_not_granted = Mock(permission_id=self.permission.pk, granted=False)
        await self.granted_permission_service.set_for_user(
            permissions=[permission_schema_not_granted],
            user=user,
        )

        is_exists = await user.granted_permissions.filter(permission_id=self.permission.pk).exists()
        assert is_exists is False


    async def test_set_for_team(self):
        team = await Team.create(name='Test')

        permission_schema = Mock(permission_id=self.permission.pk, granted=True)
        await self.granted_permission_service.set_for_team(
            permissions=[permission_schema],
            team=team,
        )

        is_exists = await team.granted_permissions.filter(permission_id=self.permission.pk).exists()
        assert is_exists is True
