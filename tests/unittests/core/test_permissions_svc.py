from tortoise.contrib.test import TestCase

from core.db.models import Module
from core.dependencies.services import get_permission_service


class TestPermissionService(TestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.permission_service = get_permission_service()
        self.module = await Module.create(name='test_module')

    async def test_create_with_scope(self):
        permission = await self.permission_service.create_with_scope(
            name='Full access',
            scope='sudo',
            module=self.module,
        )
        assert permission.scope == f"{self.module.name}:sudo"

    async def test_make_module_scope(self):
        module_scope = self.permission_service.make_module_scope(
            module_name=self.module.name,
            scope='sudo'
        )
        assert module_scope == f"{self.module.name}:sudo"

    async def test_update_or_create(self):
        created_permission = await self.permission_service.update_or_create(
            name='Full access',
            scope='sudo',
            module=self.module,
        )
        assert created_permission.name == 'Full access'

        await self.permission_service.update_or_create(
            name='Full access (updated)',
            scope='sudo',
            module=self.module,
        )
        updated_permission = await self.permission_service.get(id=created_permission.pk)
        assert updated_permission.name == 'Full access (updated)'

    async def test_delete_unused(self):
        used_permission = await self.permission_service.update_or_create(
            name='Full access',
            scope='sudo',
            module=self.module,
        )
        unused_permission = await self.permission_service.update_or_create(
            name='Unused test',
            scope='test',
            module=self.module,
        )

        await self.permission_service.delete_unused(
            module_id=self.module.pk,
            exist_ids=[used_permission.pk]
        )

        is_permission_exists = await self.permission_service.exists(id=unused_permission.pk)
        assert is_permission_exists is False
