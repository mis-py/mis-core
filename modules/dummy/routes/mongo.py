from typing import Annotated

from fastapi import Body, APIRouter, HTTPException, Depends
from starlette import status

from core.utils.schema import MisResponse
from modules.dummy.dependencies.services import get_dummy_item_service
from modules.dummy.schemas.mongo import DummyItemCreate, DummyItemUpdate, DummyItemRead
from modules.dummy.services.dummy_item import DummyItemService

router = APIRouter()


@router.post(
    "/items/",
    response_model=MisResponse[DummyItemRead],
    response_model_by_alias=False,
)
async def create_item(
        dummy_item_service: Annotated[DummyItemService, Depends(get_dummy_item_service)],
        item_in: DummyItemCreate = Body(...)
):
    new_item = await dummy_item_service.create(item_in)
    created_item = await dummy_item_service.get(id=new_item.inserted_id)
    return MisResponse[DummyItemRead](result=created_item)


@router.get(
    "/items/",
    response_model=MisResponse[list[DummyItemRead]],
    response_model_by_alias=False,
)
async def list_items(
        dummy_item_service: Annotated[DummyItemService, Depends(get_dummy_item_service)],
):
    items = await dummy_item_service.filter()
    return MisResponse[list[DummyItemRead]](result=items)


@router.get(
    "/items/{id}",
    response_model=MisResponse[DummyItemRead],
    response_model_by_alias=False,
)
async def show_item(
        dummy_item_service: Annotated[DummyItemService, Depends(get_dummy_item_service)],
        item_id: str,
):
    item = await dummy_item_service.get(id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return MisResponse[DummyItemRead](result=item)


@router.put(
    "/items/{id}",
    response_model=MisResponse[DummyItemRead],
    response_model_by_alias=False,
)
async def update_student(
        dummy_item_service: Annotated[DummyItemService, Depends(get_dummy_item_service)],
        item_id: str, item_in: DummyItemUpdate = Body(...),
):
    await dummy_item_service.update(id=item_id, schema_in=item_in)
    updated_item = await dummy_item_service.get(id=item_id)
    return MisResponse[DummyItemRead](result=updated_item)


@router.delete("/items/{id}", response_model=MisResponse)
async def delete_item(
        dummy_item_service: Annotated[DummyItemService, Depends(get_dummy_item_service)],
        item_id: str,
):
    await dummy_item_service.delete(id=item_id)
    return MisResponse(status_code=status.HTTP_204_NO_CONTENT)
