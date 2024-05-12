import datetime
import io
import os

from fastapi import APIRouter, Security
from fastapi.responses import FileResponse, StreamingResponse

from const import LOGS_DIR, TASK_LOGS_DIR
from core.db.models import Module
from core.dependencies.misc import get_current_user
from core.exceptions import MISError
from core.utils.common import find_log_file, select_logs_by_hour

router = APIRouter()


# TODO logs needs to be properly introduced
@router.get(
    "/download/app",
    dependencies=[Security(get_current_user, scopes=['core:sudo'])]
)
async def download_app_log_file(app_id: int, date: datetime.date = None, hour: int = None, display: bool = True):
    app = await Module.get(id=app_id)
    app_log_dir = LOGS_DIR / app.name
    return file_response(
        log_dir=app_log_dir,
        name=app.name,
        date=date,
        hour=hour,
        display=display,
    )


@router.get("/download/job",
            dependencies=[Security(get_current_user, scopes=['core:sudo'])])
async def download_task_log_file(job_id: str, date: datetime.date = None, hour: int = None, display: bool = True):
    job_log_dir = TASK_LOGS_DIR / job_id
    return file_response(
        log_dir=job_log_dir,
        name=job_id,
        date=date,
        hour=hour,
        display=display,
    )


def file_response(log_dir: os.path, name: str, date: datetime.date, hour: int, display: bool):
    log_file = find_log_file(
        date=date,
        name=name,
        log_dir=log_dir,
    )
    if not log_file:
        raise MISError(f"Log file for '{name}' not found")

    media_type = "text/plain" if display else "application/octet-stream"
    if hour:
        log_data = select_logs_by_hour(log_dir / log_file, hour)
        return StreamingResponse(
            content=io.StringIO(log_data),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={log_file}",
            }
        )
    else:
        return FileResponse(
            path=log_dir / log_file,
            filename=log_file,
            media_type=media_type,
        )
