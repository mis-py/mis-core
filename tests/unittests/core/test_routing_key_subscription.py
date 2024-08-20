from tortoise.contrib.test import TestCase

from core.db.models import Module, User, Team
from core.dependencies.routing_key_service import get_routing_key_subscription_service, get_routing_key_service


class TestRoutingKeySubscriptionService(TestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.routing_key_subscription_service = get_routing_key_subscription_service()
        routing_key_service = get_routing_key_service()

        module = await Module.create(name='test_module')
        team = await Team.create(name='Test')
        self.user = await User.create(username='Test', team_id=team.pk, hashed_password='...')

        self.routing_key = await routing_key_service.create_by_kwargs(
            app_id=module.pk, key='TEST_ROUTING_KEY', name='Created'
        )

    async def test_subscribe(self):
        routing_key_subscription = await self.routing_key_subscription_service.subscribe(
            user_id=self.user.pk,
            routing_key_id=self.routing_key.pk,
        )

        assert routing_key_subscription.routing_key_id == self.routing_key.pk
        assert routing_key_subscription.user_id == self.user.pk

    async def test_unsubscribe(self):
        await self.routing_key_subscription_service.subscribe(
            user_id=self.user.pk,
            routing_key_id=self.routing_key.pk,
        )
        is_exists = await self.routing_key_subscription_service.exists(
            user_id=self.user.pk,
            routing_key_id=self.routing_key.pk,
        )
        assert is_exists is True


        await self.routing_key_subscription_service.unsubscribe(
            user_id=self.user.pk,
            routing_key_id=self.routing_key.pk,
        )
        is_exists = await self.routing_key_subscription_service.exists(
            user_id=self.user.pk,
            routing_key_id=self.routing_key.pk,
        )
        assert is_exists is False
