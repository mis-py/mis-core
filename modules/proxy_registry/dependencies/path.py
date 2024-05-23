from typing import Annotated

from fastapi.params import Depends, Query

from modules.proxy_registry.dependencies.services import get_proxy_service
from modules.proxy_registry.services.proxy import ProxyService


async def get_proxy_by_id(
        proxy_service: Annotated[ProxyService, Depends(get_proxy_service)],
        proxy_id: int = Query()
):
    return await proxy_service.get_or_raise(id=proxy_id)
