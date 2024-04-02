from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IGUserPermissionRepository(IRepository, ABC):
    pass


class GUserPermissionRepository(TortoiseORMRepository, IGUserPermissionRepository):
    pass
