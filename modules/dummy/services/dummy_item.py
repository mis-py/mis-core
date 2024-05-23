from bson import ObjectId
from pydantic import BaseModel

from core.exceptions import NotFound
from modules.dummy.repositories.dummy_item import IDummyItemRepository


class DummyItemService:

    def __init__(self, dummy_item_repo: IDummyItemRepository):
        self.dummy_item_repo = dummy_item_repo

    async def get(self, id: str):
        return await self.dummy_item_repo.get(_id=ObjectId(id))

    async def filter(self, **filters):
        return await self.dummy_item_repo.filter(**filters)

    async def create(self, schema_in):
        data = schema_in.model_dump(by_alias=True, exclude=["id"])
        return await self.dummy_item_repo.create(data=data)

    async def update(self, id: str, schema_in: BaseModel):
        update_result = await self.dummy_item_repo.update(
            _id=ObjectId(id),
            data=schema_in.model_dump(by_alias=True, exclude_unset=True),
        )
        if update_result is not None:
            return update_result
        else:
            raise NotFound(f"Item {id} not found")

    async def delete(self, id: str):
        delete_result = await self.dummy_item_repo.delete(_id=ObjectId(id))
        if delete_result.deleted_count != 1:
            raise NotFound(f"Item {id} not found")
