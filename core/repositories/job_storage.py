from abc import ABC

from core.repositories.base.repository import MongodbRepository, IRepository
from libs.mongo.mongo import MongoService


class IJobStorageRepository(IRepository, ABC):
    async def filter_and_sort(self, limit: int, **filters):
        pass

    async def count(self, **filters):
        pass


class JobStorageRepository(MongodbRepository, IJobStorageRepository):
    def __init__(self):
        self.model = MongoService.database.get_collection("job_storage")
        super().__init__()

    async def filter_and_sort(self, limit: int, **filters):
        return await self.model.find(filters).sort("run_at", -1).limit(limit).to_list(length=limit)

    async def count(self, **filters):
        return await self.model.count_documents(filters)
