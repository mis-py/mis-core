from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, Any

from fastapi_pagination.bases import AbstractParams
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from tortoise import Model
from tortoise.queryset import QuerySet
from core.utils.schema import PageResponse
from fastapi_pagination.ext.tortoise import paginate as tortoise_paginate

# TODO Idea - in memory repository


class IRepository(ABC):
    model: Any = None

    @abstractmethod
    async def create(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def update(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def update_list(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def update_bulk(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def get(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def filter(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def filter_queryable(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def save(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def paginate(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def exists(self, **kwargs):
        raise NotImplementedError()


ModelType = TypeVar("ModelType", bound=Model)


class TortoiseORMRepository(IRepository):
    model: Type[ModelType] = None

    def __init__(self, model: Type[ModelType] = None):
        if not self.model:
            self.model = model

    async def create(self, data: dict) -> ModelType:
        """Create object from dict"""
        return await self.model.create(**data)

    async def update(self, data: dict, **filters) -> ModelType:
        """Update object from dict"""
        db_obj = await self.get(**filters)
        await db_obj.update_from_dict(data)
        await db_obj.save()
        return db_obj

    async def update_list(self, update_ids: list[int], data: dict) -> int:
        """Update object from dict"""
        return await self.model.filter(id__in=update_ids).update(**data)

    async def update_bulk(self, data_items: list[dict], update_fields: set[str]):
        ids = [item['id'] for item in data_items]
        objects = await self.model.filter(id__in=ids)

        id_to_obj = {obj.pk: obj for obj in objects}
        for item in data_items:
            id_obj = item.pop('id')
            obj = id_to_obj.get(id_obj)
            if not obj:
                continue
            await obj.update_from_dict(item)

        await self.model.bulk_update(objects=objects, fields=update_fields)
        return objects

    async def delete(self, **filters) -> None:
        """Delete filtered objects"""
        await self.model.filter(**filters).delete()

    async def get(self, prefetch_related: list[str] = None, **filters) -> Optional[ModelType]:
        """Get model object or None"""
        if prefetch_related is not None:
            return await self.model.get_or_none(**filters).prefetch_related(*prefetch_related)
        return await self.model.get_or_none(**filters)

    async def filter(self, prefetch_related: list[str] = None, **filters) -> list[ModelType]:
        """Returns filtered list of model objects"""
        queryset = await self.filter_queryable(prefetch_related=prefetch_related, **filters)
        return await queryset  # execute queryset

    async def filter_queryable(self, prefetch_related: list[str] = None, **filters) -> QuerySet:
        """Returns filtered queryset"""
        queryset = self.model.filter(**filters)
        if prefetch_related is not None:
            queryset = queryset.prefetch_related(*prefetch_related)
        return queryset

    async def save(self, obj: ModelType):
        """Save model object"""
        await obj.save()

    async def paginate(self, queryset: QuerySet, params: AbstractParams = None) -> PageResponse:
        """Paginate by fastapi-pagination and return pydantic model"""
        return await tortoise_paginate(queryset, params=params)

    async def exists(self, **filters) -> bool:
        """Check if model object exists"""
        return await self.model.exists(**filters)


CollectionType = TypeVar("CollectionType", bound=AsyncIOMotorCollection)


class MongodbRepository(IRepository):
    model: Type[CollectionType] = None

    def __init__(self, model: Type[CollectionType] = None):
        if self.model is None:
            self.model = model

    async def create(self, data: dict):
        return await self.model.insert_one(data)

    async def update(self, data: dict, **filters):
        return await self.model.find_one_and_update(
            filters, {"$set": data},
            return_document=ReturnDocument.AFTER
        )

    async def update_list(self, filters: dict, data: dict) -> int:
        return await self.model.update_many(filters, data)

    async def delete(self, **filters):
        return await self.model.delete_one(filters)

    async def get(self, **filters) -> Optional[ModelType]:
        return await self.model.find_one(filters)

    async def filter(self, limit: int = 100, **filters) -> list[ModelType]:
        return await self.model.find(filters).to_list(length=limit)

    async def filter_queryable(self, prefetch_related: list[str] = None, **filters) -> QuerySet:
        """Returns filtered queryset"""
        # TODO

    async def paginate(self, queryset: QuerySet, params: AbstractParams = None) -> PageResponse:
        """Paginate by fastapi-pagination and return pydantic model"""
        # TODO

    async def save(self):
        pass # TODO

    async def update_bulk(self):
        pass # TODO

    async def exists(self, **filters) -> bool:
        """Check if model object exists"""
        result = await self.model.count_documents(filters, limit=1)
        if result != 0:
            return True
        return False
