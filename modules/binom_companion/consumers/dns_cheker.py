import asyncio

from loguru import logger
from core.utils.notification.message import EventMessage

from libs.modules.AppContext import AppContext
from libs.modules.components import EventManager
from ..service import ProxyDomainService, DNSCheckerService
from ..config import RoutingKeys

routing_keys = RoutingKeys()
event_consumers = EventManager()


@event_consumers.add_consumer(routing_keys.PROXY_DOMAIN_ADDED)
async def proxy_domains_dns_record_checker(ctx: AppContext, message: EventMessage):
    """
    Checking proxy domain for DNS record 'A'
    Setting domain is valid if it has an 'A' record
    """
    # TODO need fix eventory
    # domain_data = message.json['body']
    domain_data = message.body['body']

    dns_checker_service = DNSCheckerService()
    record_to_check = 'A'
    logger.debug(f"ProxyDomain '{domain_data['name']}' starts checking.")
    # check every minute in range of 15 minutes
    for _ in range(15):
        is_valid = await dns_checker_service.check_record(domain=domain_data['name'], record=record_to_check)

        if not is_valid:
            logger.warning(f"ProxyDomain '{domain_data['name']}' still invalid. Error when check record '{record_to_check}'. Fall to sleep 60 seconds.")
            await asyncio.sleep(60)
            continue

        logger.debug(f"ProxyDomain '{domain_data['name']}' validated.")
        await ProxyDomainService().set_is_valid(domain_id=domain_data['id'])
        break

