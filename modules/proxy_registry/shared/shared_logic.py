from core.utils.module.components.shared_manager import SharedManager
from modules.proxy_registry.dependencies.services import get_proxy_service
from modules.proxy_registry.services.checker import ProxyChecker
from modules.proxy_registry.services.proxy import ProxyService

shared_manager = SharedManager()


@shared_manager.add_shared(key='get_proxy_service')
async def proxy_service() -> ProxyService:
    return get_proxy_service()


@shared_manager.add_shared(key='get_proxy_checker')
async def proxy_checker() -> ProxyChecker:
    return ProxyChecker()
