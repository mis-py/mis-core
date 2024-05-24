from core.services.base.base_service import BaseService
from modules.dummy.repositories.dummy_element import DummyElementRepository


class DummyElementService(BaseService):
    def __init__(self, dummy_element_repo: DummyElementRepository):
        self.dummy_element_repo = dummy_element_repo
        super().__init__(repo=dummy_element_repo)

    async def set_visible_by_category(self, category_id: int, is_visible: bool):
        ids_to_update = await self.dummy_element_repo.get_ids(category_id=category_id)
        await self.dummy_element_repo.update_list(
            update_ids=ids_to_update,
            data={'is_visible': is_visible},
        )
        updated_elements = await self.dummy_element_repo.filter(id__in=ids_to_update)
        return updated_elements
