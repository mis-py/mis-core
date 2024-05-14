from fastapi_pagination.bases import AbstractParams
from pydantic import BaseModel
from tortoise.queryset import QuerySet

from core.exceptions import NotFound
from core.repositories.base.repository import IRepository, ModelType
from core.utils.common import exclude_none_values
from core.utils.schema import PageResponse


class BaseService:
    """Common methods for using repositories"""

    def __init__(self, repo: IRepository) -> None:
        self.repo: IRepository = repo

    async def create(self, schema_in: BaseModel) -> ModelType:
        return await self.repo.create(data=schema_in.model_dump())

    async def create_by_kwargs(self, **kwargs) -> ModelType:
        return await self.repo.create(data=kwargs)

    async def update(self, id: int, schema_in: BaseModel) -> ModelType:
        return await self.repo.update(id=id, data=schema_in.model_dump())

    async def delete(self, **filters) -> None:
        await self.repo.delete(**filters)

    async def get(self, prefetch_related: list[str] = None, **filters) -> ModelType:
        return await self.repo.get(prefetch_related=prefetch_related, **filters)

    async def exists(self, **filters) -> bool:
        return await self.repo.exists(**filters)

    async def get_or_raise(self, prefetch_related: list[str]= None, **filters) -> ModelType:
        model_object = await self.repo.get(prefetch_related=prefetch_related, **filters)
        if not model_object:
            raise NotFound(f"{self.repo.model.__name__} not found")
        return model_object

    async def filter(self, prefetch_related: list[str] = None, **filters) -> list[ModelType]:
        filters_without_none = exclude_none_values(filters)
        return await self.repo.filter(
            prefetch_related=prefetch_related, **filters_without_none)

    async def filter_queryable(self, prefetch_related: list[str] = None, **filters) -> QuerySet:
        filters_without_none = exclude_none_values(filters)
        return await self.repo.filter_queryable(
            prefetch_related=prefetch_related, **filters_without_none)

    async def filter_and_paginate(
            self, prefetch_related: list[str] = None, params: AbstractParams = None, **filters
    ) -> PageResponse:
        queryset = await self.filter_queryable(prefetch_related, **filters)
        return await self.repo.paginate(queryset=queryset, params=params)
