from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IGrantedPermissionRepository(IRepository, ABC):
    pass


class GrantedPermissionRepository(TortoiseORMRepository, IGrantedPermissionRepository):
    pass
