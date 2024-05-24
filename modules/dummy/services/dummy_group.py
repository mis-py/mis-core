from core.services.base.base_service import BaseService
from modules.dummy.repositories.dummy_group import DummyGroupRepository


class DummyGroupService(BaseService):
    def __init__(self, dummy_group_repo: DummyGroupRepository):
        self.dummy_group_repo = dummy_group_repo
        super().__init__(repo=dummy_group_repo)

    async def filter_with_elements_and_paginate(self, params, **filters):
        queryset = await self.dummy_group_repo.filter_queryable_with_elements(**filters)
        return await self.dummy_group_repo.paginate(queryset, params=params)
