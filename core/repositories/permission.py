from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IPermissionRepository(IRepository, ABC):
    pass


class PermissionRepository(TortoiseORMRepository, IPermissionRepository):
    pass
