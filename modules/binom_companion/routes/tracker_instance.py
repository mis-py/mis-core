import loguru
from fastapi import APIRouter, Security

from core.dependencies.security import get_current_user
from core.utils.schema import PageResponse, MisResponse

from ..schemas.tracker_instance import TrackerInstanceModel, TrackerInstanceCreateModel, TrackerInstanceUpdateModel
from ..service import TrackerInstanceService

router = APIRouter(
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'binom_companion:replacement_groups'])],
)


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


@router.get(
    '/get',
    response_model=MisResponse[TrackerInstanceModel]
)
async def get_tracker_instance(tracker_instance_id: int):
    tracker_instance = await TrackerInstanceService().get(
        id=tracker_instance_id,
        prefetch_related=[
            'replacement_history'
        ]
    )

    return MisResponse[TrackerInstanceModel](result=tracker_instance)


@router.put(
    '/edit',
    response_model=MisResponse[TrackerInstanceModel]
)
async def edit_tracker_instance(
        tracker_instance_id: int,
        tracker_instance_in: TrackerInstanceUpdateModel,
):
    tracker_instance = await TrackerInstanceService().update(
        id=tracker_instance_id,
        schema_in=tracker_instance_in
    )

    await tracker_instance.fetch_related("replacement_groups")

    return MisResponse[TrackerInstanceModel](result=tracker_instance)


@router.delete(
    '/remove',
    response_model=MisResponse
)
async def delete_tracker_instance(tracker_instance_id: int):
    await TrackerInstanceService().delete(id=tracker_instance_id)

    return MisResponse()


@router.get(
    '/check',
    response_model=MisResponse[bool]
)
async def check_connection_tracker_instance(tracker_instance_id: int):
    check_result = await TrackerInstanceService().check_connection(tracker_instance_id)

    return MisResponse[bool](result=check_result)
