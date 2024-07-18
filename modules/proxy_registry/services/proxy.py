from core.services.base.base_service import BaseService
from modules.proxy_registry.repositories.proxy import IProxyRepository


class ProxyService(BaseService):
    def __init__(self, proxy_repo: IProxyRepository):
        self.proxy_repo = proxy_repo
        super().__init__(repo=proxy_repo)

    async def toggle_is_enabled(self, proxy_id: int, current_is_enabled: bool):
        new_is_enabled = not current_is_enabled
        proxy = await self.proxy_repo.update(id=proxy_id, data={'is_enabled': new_is_enabled})
        return proxy

    async def filter_by_ids(self, proxy_ids: list[int]):
        return await self.filter(id__in=proxy_ids)
