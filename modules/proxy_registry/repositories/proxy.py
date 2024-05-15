from abc import ABC, abstractmethod

from modules.proxy_registry.db.models import Proxy
from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IProxyRepository(IRepository, ABC):
    pass


class ProxyRepository(TortoiseORMRepository, IProxyRepository):
    model = Proxy
