from typing import Annotated

from fastapi import Depends

from core.exceptions import NotFound
from modules.binom_companion.dependencies.services import get_tracker_instance_service
from modules.binom_companion.services.tracker_instance import TrackerInstanceService


async def get_tracker_instance_by_id(
        tracker_instance_service: Annotated[TrackerInstanceService, Depends(get_tracker_instance_service)],
        tracker_instance_id: int,
):
    tracker_instance = await tracker_instance_service.get(id=tracker_instance_id)
    if not tracker_instance:
        raise NotFound('TrackerInstance not found')
    return tracker_instance