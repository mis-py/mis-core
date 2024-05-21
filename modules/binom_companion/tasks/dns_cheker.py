from loguru import logger

from libs.modules.AppContext import AppContext
from libs.modules.components import ScheduledTasks
from ..service import ProxyDomainService, DNSCheckerService

scheduled_tasks = ScheduledTasks()


@scheduled_tasks.schedule_task(trigger=None)
async def proxy_domains_dns_record_checker(ctx: AppContext):
    """
    Checking all valid proxy domains for DNS record 'A'
    Setting domain invalid if not 'A' record
    """

    active_proxy_domains = await ProxyDomainService().filter(is_invalid=False)
    dns_checker_service = DNSCheckerService()
    record_to_check = 'A'

    for domain in active_proxy_domains:
        is_valid = await dns_checker_service.check_record(domain=domain.name, record=record_to_check)
        if is_valid:
            continue

        await ProxyDomainService().set_invalid(domain_id=domain.pk)
        logger.warning(f"ProxyDomain '{domain.name}' invalid. Error when check record '{record_to_check}'")

