from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IModuleRepository(IRepository, ABC):
    pass


class ModuleRepository(TortoiseORMRepository, IModuleRepository):
    pass
