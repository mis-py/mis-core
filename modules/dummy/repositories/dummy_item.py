from abc import ABC

from core.repositories.base.repository import MongodbRepository, IRepository
from libs.mongo.mongo import MongoService


class IDummyItemRepository(IRepository, ABC):
    pass


class DummyItemRepository(MongodbRepository, IDummyItemRepository):
    model = MongoService.database.get_collection("dummy_items")
