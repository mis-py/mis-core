from loguru import logger
from tortoise.exceptions import IntegrityError

from core.dependencies.services import get_routing_key_service
from core.services.notification import RoutingKeyService
from ..Base.BaseComponent import BaseComponent


class EventRoutingKeys(BaseComponent):
    async def pre_init(self, application):
        pass

    def __init__(self, routing_keys):
        self.routing_keys = routing_keys

    async def init(self, app_db_model, is_created: bool):
        await self.save_routing_keys(app_db_model)
        logger.debug(f'[RoutingKey] Routing keys saved for {self.module.name}')

    async def start(self):
        pass

    async def stop(self):
        pass

    async def shutdown(self):
        pass

    async def save_routing_keys(self, app_model):
        routing_key_service: RoutingKeyService = get_routing_key_service()
        for key, value in self.routing_keys:
            routing_key = await routing_key_service.get(app_id=app_model.pk, key=key, name=value)
            if routing_key:
                logger.debug(f'[RoutingKey] Routing key {key} already created for {self.module.name}')
                continue

            try:
                await routing_key_service.recreate(module_id=app_model.pk, key=key, name=value)
                logger.debug(f'[RoutingKey] Created routing key {key} for {self.module.name}')
            except IntegrityError as error:
                logger.error(f'[RoutingKey] Routing key {key} create error: {error} for {self.module.name}')

        # TODO rk is removing right after they created. fix it
        # deleted_num = await routing_key_service.delete_unused(
        #     module_id=app_model.pk,
        #     exist_keys=[value for key, value in self.routing_keys]
        # )
        #
        # logger.debug(f'[RoutingKey] Deleted {deleted_num} unused routing keys for {self.module.name}')
