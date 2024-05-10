from abc import ABC

from core.db.guardian import GuardianContentType
from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IGContentTypeRepository(IRepository, ABC):
    pass


class GContentTypeRepository(TortoiseORMRepository, IGContentTypeRepository):
    model = GuardianContentType
