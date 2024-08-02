from loguru import logger

from datetime import datetime, timedelta, timezone

from core.utils.app_context import AppContext
from core.utils.module.components import ScheduledTasks
from ..service import LeadRecordService

scheduled_tasks = ScheduledTasks()


# cleanup for old lead records
@scheduled_tasks.schedule_task(
    seconds=60,
    start_date=datetime.now() + timedelta(seconds=10)
)
async def old_lead_records_cleanup(
        logger,
        lead_record_ttl: int = 1800,
        **kwargs,
):
    now = datetime.now(timezone.utc)

    query = await LeadRecordService().filter_queryable(
        time__lte=now - timedelta(seconds=lead_record_ttl)
    )
    num_deleted = await query.delete()

    logger.debug(f'Deleted {num_deleted} LeadRecords')
