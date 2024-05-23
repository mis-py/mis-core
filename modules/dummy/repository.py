from core.repositories.base.repository import TortoiseORMRepository
from modules.dummy.db.models import DummyModel


class DummyRepository(TortoiseORMRepository):
    model = DummyModel
