from typing import Annotated

import loguru
from fastapi import APIRouter, Security, Depends

from core.dependencies.security import get_current_user
from core.utils.schema import PageResponse, MisResponse
from ..db.models import TrackerInstance
from ..dependencies.path import get_tracker_instance_by_id
from ..dependencies.services import get_tracker_instance_service

from ..schemas.tracker_instance import TrackerInstanceModel, TrackerInstanceCreateModel, TrackerInstanceUpdateModel
from ..services.tracker import get_tracker_service
from ..services.tracker_instance import TrackerInstanceService

router = APIRouter(
    dependencies=[Security(get_current_user, scopes=[
        'binom_companion:sudo',
        'binom_companion:tracker_instance'
    ])],
)


@router.get(
    '',
    response_model=PageResponse[TrackerInstanceModel]
)
async def get_tracker_instances(
    tracker_instance_service: Annotated[TrackerInstanceService, Depends(get_tracker_instance_service)],
):
    return await tracker_instance_service.filter_and_paginate(
        prefetch_related=['replacement_groups']
    )


@router.post(
    '/add',
    response_model=MisResponse[TrackerInstanceModel]
)
async def create_tracker_instance(
        tracker_in: TrackerInstanceCreateModel,
        tracker_instance_service: Annotated[TrackerInstanceService, Depends(get_tracker_instance_service)],
):
    tracker_instance = await tracker_instance_service.create(tracker_in)

    await tracker_instance.fetch_related("replacement_groups")

    return MisResponse[TrackerInstanceModel](result=tracker_instance)


@router.get(
    '/get',
    response_model=MisResponse[TrackerInstanceModel]
)
async def get_tracker_instance(
        tracker_instance_id: int,
        tracker_instance_service: Annotated[TrackerInstanceService, Depends(get_tracker_instance_service)],
):
    tracker_instance = await tracker_instance_service.get(
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
        tracker_instance_in: TrackerInstanceUpdateModel,
        tracker_instance_service: Annotated[TrackerInstanceService, Depends(get_tracker_instance_service)],
        tracker_instance: TrackerInstance = Depends(get_tracker_instance_by_id),
):
    tracker_instance = await tracker_instance_service.update(
        id=tracker_instance.pk,
        schema_in=tracker_instance_in
    )

    await tracker_instance.fetch_related("replacement_groups")

    return MisResponse[TrackerInstanceModel](result=tracker_instance)


@router.delete(
    '/remove',
    response_model=MisResponse
)
async def delete_tracker_instance(
        tracker_instance_service: Annotated[TrackerInstanceService, Depends(get_tracker_instance_service)],
        tracker_instance: TrackerInstance = Depends(get_tracker_instance_by_id),
):
    await tracker_instance_service.delete(id=tracker_instance.pk)

    return MisResponse()


@router.get(
    '/check',
    response_model=MisResponse[dict]
)
async def check_connection_tracker_instance(
        tracker_instance: TrackerInstance = Depends(get_tracker_instance_by_id),
):
    tracker_service = get_tracker_service(tracker_instance.tracker_type)
    check_result = await tracker_service.check_connection(tracker_instance)

    return MisResponse[dict](result=check_result)
