from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IGPermissionRepository(IRepository, ABC):
    pass


class GPermissionRepository(TortoiseORMRepository, IGPermissionRepository):
    pass
