from modules.proxy_registry.repositories.proxy import ProxyRepository
from modules.proxy_registry.services.proxy import ProxyService


def get_proxy_service() -> ProxyService:
    proxy_repo = ProxyRepository()

    proxy_service = ProxyService(proxy_repo=proxy_repo)
    return proxy_service
