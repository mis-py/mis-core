from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IGContentTypeRepository(IRepository, ABC):
    pass


class GContentTypeRepository(TortoiseORMRepository, IGContentTypeRepository):
    pass
