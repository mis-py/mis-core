from core.services.base.base_service import BaseService
from modules.dummy.repositories.dummy_restricted import DummyRestrictedRepository


class DummyRestrictedService(BaseService):
    def __init__(self, dummy_restricted_repo: DummyRestrictedRepository):
        self.dummy_restricted_repo = dummy_restricted_repo
        super().__init__(repo=dummy_restricted_repo)
