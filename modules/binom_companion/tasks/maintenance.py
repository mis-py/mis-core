from loguru import logger

from services.modules.components import ScheduledTasks
from datetime import datetime, timedelta, timezone

from services.modules.context import AppContext

from ..service import LeadRecordService

scheduled_tasks = ScheduledTasks()


# cleanup for old lead records
@scheduled_tasks.schedule_task(
    seconds=60,
    start_date=datetime.now() + timedelta(seconds=10)
)
async def old_lead_records_cleanup(ctx: AppContext):
    lead_record_ttl = ctx.variables.LEAD_RECORD_TTL
    now = datetime.now(timezone.utc)

    num_deleted = await LeadRecordService().filter(
        time__lte=now - timedelta(seconds=lead_record_ttl)
    ).delete()

    logger.debug(f'Deleted {num_deleted} LeadRecords')