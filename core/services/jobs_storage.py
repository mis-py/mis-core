from enum import Enum

from tortoise import timezone

from bson import ObjectId

from core.exceptions import NotFound
from core.repositories.job_storage import IJobStorageRepository, JobStorageRepository


class JobStorageService:

    def __init__(self, job_storage_repo: IJobStorageRepository):
        self.job_storage_repo = job_storage_repo

    async def get(self, id: str):
        return await self.job_storage_repo.get(_id=ObjectId(id))

    async def filter_and_sort(self, limit: int, **filters):
        return await self.job_storage_repo.filter_and_sort(**filters, limit=limit)

    async def create(self, data):
        return await self.job_storage_repo.create(data=data)

    async def update(self, id: str, data: dict):
        update_result = await self.job_storage_repo.update(
            _id=ObjectId(id),
            data=data,
        )
        if update_result is not None:
            return update_result
        else:
            raise NotFound(f"Item {id} not found")

    async def count(self, **filters):
        return await self.job_storage_repo.count(**filters)


class JobStatus(str, Enum):
    WAITING = "waiting"
    EXECUTING = "executing"
    FAILED = "failed"
    DONE = "done"


class JobExecutionStorage:

    def __init__(self):
        self.job_storage_service = JobStorageService(job_storage_repo=JobStorageRepository())

    async def insert(self, job_id: int):
        new_item = await self.job_storage_service.create(
            data={
                'job_id': job_id,
                'status': JobStatus.EXECUTING.value,
                'run_at': timezone.now(),
                'yield': [],
                'return': None,
                'exception': None,
                'end_at': None,
                'time': None,
            }
        )
        return new_item.inserted_id

    async def insert_yield(self, item_id: int, value):
        """Insert yield value for execution item"""
        item = await self.job_storage_service.get(id=item_id)
        force_str_value = str(value)
        item['yield'].append(force_str_value)
        await self.job_storage_service.update(id=item_id, data=item)

    async def set_return(self, item_id: str, value):
        """Set return value for execution item"""
        item = await self.job_storage_service.get(id=item_id)
        force_str_value = str(value)
        item['return'] = force_str_value
        await self.job_storage_service.update(id=item_id, data=item)

    async def set_exception(self, item_id: str, value):
        """Set exception value for execution item"""
        item = await self.job_storage_service.get(id=item_id)
        force_str_value = str(value)
        item['exception'] = force_str_value
        item['status'] = JobStatus.FAILED.value
        await self.job_storage_service.update(id=item_id, data=item)

    async def set_end(self, item_id: str):
        """Set end info for execution item"""
        item = await self.job_storage_service.get(id=item_id)
        item['end_at'] = timezone.now()
        item['status'] = JobStatus.DONE.value
        await self.job_storage_service.update(id=item_id, data=item)

    async def set_time_execution(self, item_id: str, seconds: float):
        """Set execution seconds for execution item"""
        item = await self.job_storage_service.get(id=item_id)
        item['time'] = seconds
        await self.job_storage_service.update(id=item_id, data=item)

    async def get(self, job_id: int, limit: int = 20):
        executions = await self.job_storage_service.filter_and_sort(job_id=job_id, limit=limit)
        if not executions:
            return {
                'count': 0,
                'items': [],
            }

        clear_execution_items = []
        for item in executions:
            item.pop('_id')
            item.pop('job_id')
            clear_execution_items.append(item)

        return {
            'count': await self.job_storage_service.count(job_id=job_id),
            'items': clear_execution_items,
        }
