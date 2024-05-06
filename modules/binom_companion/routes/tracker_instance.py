import loguru
from fastapi import APIRouter

from core.utils.schema import PageResponse, MisResponse

from ..schemas.tracker_instance import TrackerInstanceModel, TrackerInstanceCreateModel
from ..service import TrackerInstanceService

router = APIRouter()


@router.get(
    '',
    response_model=PageResponse[TrackerInstanceModel]
)
async def get_tracker_instances():
    return await TrackerInstanceService().filter_and_paginate(
        prefetch_related=['replacement_groups']
    )


@router.post(
    '/add',
    response_model=MisResponse[TrackerInstanceModel]
)
async def create_tracker_instance(tracker_in: TrackerInstanceCreateModel):
    tracker_instance = await TrackerInstanceService().create(tracker_in)

    await tracker_instance.fetch_related("replacement_groups")

    return MisResponse[TrackerInstanceModel](result=tracker_instance)
