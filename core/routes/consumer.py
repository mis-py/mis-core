from aiormq import DuplicateConsumerTag
from fastapi import APIRouter, Security, Response

from core.dependencies.misc import get_current_user
from core.exceptions import NotFound, AlreadyExists

from libs.eventory import Eventory


router = APIRouter(dependencies=[
    Security(get_current_user, scopes=['core:sudo', 'core:consumers']),
])

# TODO do i actually need that??
# currently not changing it coz it may be not needed


@router.get('')
def get_consumers():
    res = {}
    for app_name, consumer in Eventory.iter_consumers():
        res.setdefault(app_name, []).append({
            'consumer_tag': consumer.consumer_tag,
            'queue': consumer.queue.name,
            'status': consumer.status,
            'receiver': consumer.receiver.__name__,
        })
    return res


@router.post('/pause')
async def pause_consumer(consumer_tag: str):
    if not await Eventory.pause_consumer(consumer_tag):
        raise NotFound("Consumer not found")
    return Response(status_code=200)


@router.post('/resume')
async def resume_consumer(consumer_tag: str):
    try:
        if not await Eventory.resume_consumer(consumer_tag):
            raise NotFound("Consumer not found")
    except DuplicateConsumerTag:
        return AlreadyExists(f"Consumer '{consumer_tag}' already running")
    return Response(status_code=200)
