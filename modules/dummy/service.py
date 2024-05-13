from core.services.base.base_service import BaseService

from .db.models import DummyModel
from .repository import DummyRepository


class DummyService(BaseService):
    def __init__(self):
        super().__init__(repo=DummyRepository(model=DummyModel))
