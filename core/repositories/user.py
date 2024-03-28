from abc import ABC

from core.repositories.base.repository import IRepository, TortoiseORMRepository


class IUserRepository(IRepository, ABC):
    pass


class UserRepository(TortoiseORMRepository, IUserRepository):
    pass
