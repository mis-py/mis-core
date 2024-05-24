from pydantic import BaseModel

from core.services.base.base_service import BaseService
from modules.dummy.repositories.dummy_element import DummyElementRepository


class DummyElementService(BaseService):
    def __init__(self, dummy_element_repo: DummyElementRepository):
        self.dummy_element_repo = dummy_element_repo
        super().__init__(repo=dummy_element_repo)
