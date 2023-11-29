from typing import Type, Optional, TypeVar

from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model
from tortoise.queryset import QuerySet

from core.exceptions import NotFound

ModelType = TypeVar("ModelType", bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase:
    """Base CRUD class"""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, **kwargs) -> Optional[ModelType]:
        """Get model object or None"""
        return await self.model.filter(**kwargs).first()

    async def get_or_raise(self, **kwargs) -> Optional[ModelType]:
        """Get model object or raise"""
        try:
            return await self.model.get(**kwargs)
        except DoesNotExist as error:
            raise NotFound(str(error))

    async def query_get_multi(self, skip: int = 0, limit: int = 100, **kwargs) -> QuerySet:
        """Return QuerySet with pagination and filter by kwargs"""
        query = self.model.all()

        # removing None values from kwargs
        # helpful for filtering by optional query params in endpoints
        kwargs_without_none = {key: value for key, value in kwargs.items() if value is not None}

        return query.offset(skip).limit(limit).filter(**kwargs_without_none).order_by('id')

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create object from pydantic schema"""
        obj_in_data = obj_in.model_dump()
        obj = await self.model.create(**obj_in_data)
        return obj

    async def update(self, db_obj: ModelType, obj_in: UpdateSchemaType | dict) -> ModelType:
        """Update object from pydantic schema or dict"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        await db_obj.update_from_dict(update_data).save()
        return db_obj

    async def remove(self, **kwargs) -> None:
        """Remove one object"""
        obj = await self.model.get(**kwargs)
        await obj.delete()

    async def remove_list(self, **kwargs) -> None:
        """Remove list of objects"""
        await self.model.filter(**kwargs).delete()
