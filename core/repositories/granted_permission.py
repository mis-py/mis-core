from abc import ABC

from core.db.permission import GrantedPermission
from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IGrantedPermissionRepository(IRepository, ABC):
    pass


class GrantedPermissionRepository(TortoiseORMRepository, IGrantedPermissionRepository):
    model = GrantedPermission
