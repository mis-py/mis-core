from loguru import logger

from fastapi import APIRouter, Depends, Security, Response

from core.db import User
from core.db.crud import crud_jobs
from core.dependencies import get_current_user
from core.exceptions import NotFound

from services.scheduler import SchedulerService

from .schema import JobSchema, JobSchedule, JobAdd
# from .dependencies import get_scheduler_service
from .utils import format_trigger, make_trigger


router = APIRouter(dependencies=[
    Security(get_current_user, scopes=['core:sudo', 'core:tasks']),
])


@router.get('/all', response_model=list[JobSchema])
async def get_jobs(
        task_id: str = None,
        user_id: str = None,
        team_id: str = None,
        # scheduler: SchedulerService = Depends(get_scheduler_service),
):
    """
    Get existent task jobs
    :param task_id: Return jobs from specific task_id
    :param user_id: Return jobs from specific user_id, can not be used with team_id
    :param team_id: Return jobs from specific team_id, can not be used with user_id
    """
    response = []

    if user_id and team_id:
        return response

    saved_jobs_dict = await crud_jobs.get_scheduled_jobs_dict()

    for job in SchedulerService.get_jobs():

        saved_job = saved_jobs_dict.get(job.id)

        if not saved_job:
            logger.error("Job not in saved jobs!")
            continue

        # filter jobs by task
        if task_id and task_id not in job.id:
            continue

        # TODO verify it
        if user_id and user_id != saved_job.user:
            continue

        if team_id and team_id != saved_job.team:
            continue

        response.append(
            JobSchema(
                id=job.id,
                name=job.name,
                status=saved_job.status,
                next_run_time=job.next_run_time,
                trigger=format_trigger(job.trigger),
                app=saved_job.app.name,
                user=saved_job.user,
                team=saved_job.team,
            )
        )
    return response


@router.get('/single', response_model=JobSchema)
async def get_single_job(
        job_id: str = None,
        # scheduler: SchedulerService = Depends(get_scheduler_service),
        current_user: User = Depends(get_current_user)
):
    job = SchedulerService.get_job(job_id)

    saved_job = await crud_jobs.get_scheduled_job(job_id, current_user)
    if not saved_job:
        raise NotFound("Saved scheduled job not found!")

    return JobSchema(
        id=job.id,
        name=job.name,
        status=saved_job.status,
        next_run_time=job.next_run_time,
        trigger=format_trigger(job.trigger),
        app=saved_job.app.name,
        user=saved_job.user,
        team=saved_job.team,
    )


@router.post('/add')
async def add_job(
        task_id: str,
        data: JobAdd = None,
        # scheduler: SchedulerService = Depends(get_scheduler_service),
        current_user: User = Depends(get_current_user),
):
    if data:
        extra = data.extra
        trigger = make_trigger(data.trigger) if data.trigger else None
    else:
        extra = None
        trigger = None

    job = await SchedulerService.add_job(task_id, current_user, extra=extra, trigger=trigger)

    if data and data.trigger:
        await crud_jobs.save_schedule_job_trigger(job.id, data.trigger)

    return Response(status_code=200)


@router.post('/pause')
async def pause_job(
        job_id: str,
        # scheduler: SchedulerService = Depends(get_scheduler_service),
        current_user: User = Depends(get_current_user)
):
    await SchedulerService.pause_job(job_id, current_user)
    return Response(status_code=200)


@router.post('/resume')
async def resume_job(
        job_id: str,
        # scheduler: SchedulerService = Depends(get_scheduler_service),
        current_user: User = Depends(get_current_user)
):
    await SchedulerService.resume_job(job_id, current_user)
    return Response(status_code=200)


@router.post('/reschedule')
async def reschedule_job(
        job_id: str,
        schedule_data: JobSchedule,
        # scheduler: SchedulerService = Depends(get_scheduler_service),
):

    job = SchedulerService.get_job(job_id)

    trigger = make_trigger(schedule_data)

    job.reschedule(trigger=trigger)

    await crud_jobs.save_schedule_job_trigger(job.id, schedule_data)
    return Response(status_code=200)


@router.delete('/remove')
async def remove_job(
        job_id: str,
        # scheduler: SchedulerService = Depends(get_scheduler_service),
        current_user: User = Depends(get_current_user)
):
    await SchedulerService.remove_job(job_id, current_user)
    return Response(status_code=200)
