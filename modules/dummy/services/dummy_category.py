from core.services.base.base_service import BaseService
from modules.dummy.repositories.dummy_category import DummyCategoryRepository


class DummyCategoryService(BaseService):
    def __init__(self, dummy_category_repo: DummyCategoryRepository):
        self.dummy_category_repo = dummy_category_repo
        super().__init__(repo=dummy_category_repo)
