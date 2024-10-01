from tortoise.contrib.test import TestCase

from core.db.models import Module
from core.dependencies.routing_key_service import get_routing_key_service


class TestRoutingKeyService(TestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.routing_key_service = get_routing_key_service()
        self.module = await Module.create(name='test_module')

    async def test_recreate(self):
        created_routing_key = await self.routing_key_service.create_by_kwargs(
            app_id=self.module.pk, key='TEST_ROUTING_KEY', name='Created'
        )

        recreate_routing_key = await self.routing_key_service.recreate(
            module_id=self.module.pk, key='TEST_ROUTING_KEY', name='Recreated'
        )

        assert created_routing_key.pk != recreate_routing_key.pk
        assert recreate_routing_key.name == 'Recreated'

        is_exists = await self.routing_key_service.exists(id=created_routing_key.pk)
        assert is_exists is False

    async def test_delete_unused(self):
        used_routing_key = await self.routing_key_service.create_by_kwargs(
            app_id=self.module.pk, key='USED_TEST_ROUTING_KEY', name='USED_TEST_ROUTING_KEY'
        )
        unused_routing_key = await self.routing_key_service.create_by_kwargs(
            app_id=self.module.pk, key='UNUSED_ROUTING_KEY', name='UNUSED_ROUTING_KEY'
        )

        await self.routing_key_service.delete_unused(
            module_id=self.module.pk,
            exist_keys=[used_routing_key.key]
        )

        is_exists_used_routing_key = await self.routing_key_service.exists(id=used_routing_key.pk)
        assert is_exists_used_routing_key is True

        is_exists_unused_routing_key = await self.routing_key_service.exists(id=unused_routing_key.pk)
        assert is_exists_unused_routing_key is False

    async def test_make_routing_keys_set(self):
        await self.routing_key_service.create_by_kwargs(
            app_id=self.module.pk, key='TEST_ROUTING_KEY', name='TEST_ROUTING_KEY'
        )

        routing_key_set = await self.routing_key_service.make_routing_keys_set(self.module)

        assert routing_key_set.TEST_ROUTING_KEY == 'TEST_ROUTING_KEY'


    async def test_body_verbose_by_template(self):
        template_string = await self.routing_key_service.body_verbose_by_template(
            body={"name": "test"}, template_string="Template name: $name",
        )
        assert template_string == "Template name: test"

