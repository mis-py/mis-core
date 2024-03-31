from abc import ABC

from core.repositories.base.repository import IRepository, TortoiseORMRepository


class IVariableRepository(IRepository, ABC):
    pass


class VariableRepository(TortoiseORMRepository, IVariableRepository):
    pass
