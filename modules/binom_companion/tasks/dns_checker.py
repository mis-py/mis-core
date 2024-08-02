from loguru import logger

from core.utils.app_context import AppContext
from core.utils.module.components import ScheduledTasks
from ..service import ProxyDomainService, DNSCheckerService

scheduled_tasks = ScheduledTasks()


@scheduled_tasks.schedule_task(trigger=None)
async def proxy_domains_checker(ctx: AppContext, logger, **kwargs):
    """
    Checking all valid proxy domains for DNS record 'A'
    Setting domain invalid if not 'A' record
    """
    logger.debug(f"Start domain validating!")
    proxy_domain_service = ProxyDomainService(context_logger=logger)
    active_proxy_domains = await proxy_domain_service.filter(is_invalid=True)
    dns_checker_service = DNSCheckerService()
    record_to_check = 'A'
    logger.debug(f"Domains to check: '{active_proxy_domains}'")
    for domain in active_proxy_domains:
        logger.debug(f"Start validating: {domain.name}")
        is_valid = await dns_checker_service.check_record(domain=domain.name, record=record_to_check)
        if is_valid:
            logger.debug(f"ProxyDomain: '{domain.name}' validated by DNS")

            class Proxy:
                name: str = 'without'

            proxy = Proxy()

            is_checked = await proxy_domain_service.is_domain_ok_by_proxy(domain.name, proxy)

            if is_checked:
                await proxy_domain_service.set_is_valid(domain_id=domain.id)
                logger.success(f"ProxyDomain: '{domain.name}' validated by PROXY")
            else:
                logger.warning(f"ProxyDomain: '{domain.name}' validation by PROXY failed")

        else:
            logger.warning(f"ProxyDomain: '{domain.name}' validation by DNS failed")

    logger.debug(f"Task finished.")
