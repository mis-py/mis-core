import loguru
from pydantic import BaseModel, Field, computed_field, field_serializer, model_serializer, field_validator, TypeAdapter, validator
from typing import Generic, TypeVar, Type, Optional, Sequence, Any, Dict
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from fastapi_pagination.types import Cursor, GreaterEqualZero, ParamsType, GreaterEqualOne
from fastapi_pagination.utils import create_pydantic_model
from fastapi import Query, status
from typing_extensions import Self
from math import ceil


class MisModel(BaseModel):
    model_config = {
        "from_attributes": True,
    }


T = TypeVar('T', bound=BaseModel)


class BaseResponse(BaseModel, Generic[T]):
    status_code: int = Field(default=status.HTTP_200_OK)
    msg: str = Field(default="Success")

    @computed_field
    @property
    def status(self) -> bool:
        return self.status_code == 200


# https://uriyyo-fastapi-pagination.netlify.app/
# https://github.com/uriyyo/fastapi-pagination/issues/296
# https://github.com/uriyyo/fastapi-pagination/issues/308
# https://github.com/uriyyo/fastapi-pagination/issues/362
# https://github.com/uriyyo/fastapi-pagination/issues/590
# https://github.com/uriyyo/fastapi-pagination/issues/788
class Params(BaseModel, AbstractParams):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(50, ge=50, le=1500, description="Page size")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.size if self.size is not None else None,
            offset=self.size * (self.page - 1) if self.page is not None and self.size is not None else None,
        )


class ResponsePageData(BaseModel, Generic[T]):
    total: int
    current: Optional[GreaterEqualOne]
    size: Optional[GreaterEqualOne]
    pages: Optional[GreaterEqualZero] = None
    items: Sequence[T]


class PageResponse(AbstractPage[T], BaseResponse[T]):
    result: ResponsePageData[T]
    __params_type__ = Params

    @classmethod
    def create(cls, items: Sequence[T], params: AbstractParams, total: Optional[int] = None) -> Self:
        assert isinstance(params, Params)
        assert total is not None

        size = params.size if params.size is not None else (total or None)
        page = params.page if params.page is not None else 1

        if size in {0, None}:
            pages = 0
        elif total is not None:
            pages = ceil(total / size)
        else:
            pages = None

        return create_pydantic_model(
            cls,
            result={
                "items": items,
                "total": total,
                "current": page,
                "size": size,
                "pages": pages,
            },
            # result=PageData(
            #     items=items,
            #     total=total,
            #     current=page,
            #     size=size,
            #     pages=pages
            # )
        )


class MisResponse(BaseResponse[T]):
    result: Optional[T] = Field(default={})

