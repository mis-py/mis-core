from modules.proxy_registry.dependencies.services import get_proxy_service
from modules.proxy_registry.services.checker import ProxyChecker
from modules.proxy_registry.services.proxy import ProxyService


async def proxy_service() -> ProxyService:
    return get_proxy_service()


async def proxy_checker() -> ProxyChecker:
    return ProxyChecker()
