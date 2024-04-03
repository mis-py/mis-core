from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional

from fastapi_pagination.bases import AbstractParams
from tortoise import Model
from tortoise.queryset import QuerySet
from core.utils.schema import PageResponse
from fastapi_pagination.ext.tortoise import paginate as tortoise_paginate


class IRepository(ABC):
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


ModelType = TypeVar("ModelType", bound=Model)


class TortoiseORMRepository(IRepository):

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, data: dict) -> ModelType:
        """Create object from dict"""
        return await self.model.create(**data)

    async def update(self, data: dict, **filters) -> ModelType:
        """Update object from dict"""
        db_obj = await self.get(**filters)
        await db_obj.update_from_dict(data)
        return db_obj

    async def update_list(self, update_ids: list[str], data: dict) -> int:
        """Update object from dict"""
        return await self.model.filter(id__in=update_ids).update(**data)

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
