from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IGGroupPermissionRepository(IRepository, ABC):
    pass


class GGroupPermissionRepository(TortoiseORMRepository, IGGroupPermissionRepository):
    pass
