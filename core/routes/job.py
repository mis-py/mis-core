from loguru import logger

from fastapi import APIRouter, Depends, Security, Response

from core.db.models import User
from core.dependencies import get_current_user
from core.dependencies.misc import UnitOfWorkDep
from core.exceptions import NotFound
from core.services.scheduled_job import ScheduledJobService

from services.scheduler import SchedulerService

from core.schemas.task import JobResponse, JobScheduleUpdate, JobCreate
from core.utils.task import format_trigger, make_trigger
from core.utils.schema import MisResponse, PageResponse

router = APIRouter(dependencies=[
    Security(get_current_user, scopes=['core:sudo', 'core:tasks']),
])


@router.get(
    '/all',
    response_model=MisResponse[list[JobResponse]]
)
async def get_jobs(
        uow: UnitOfWorkDep,
        task_id: str = None,
        user_id: str = None,
        team_id: str = None,
        job_id: str = None,
        current_user: User = Depends(get_current_user)
):
    """
    Get existent jobs
    :param task_id: Return jobs from specific task_id, can not be used with other *_id
    :param user_id: Return jobs from specific user_id, can not be used with other *_id
    :param team_id: Return jobs from specific team_id, can not be used with other *_id
    :param job_id: Return job for specific job_id, can not be used with other *_id
    """
    response = []

    if sum(1 for item in [task_id, user_id, team_id, job_id] if item is None) > 1:
        logger.error("Specified more than one filter!")
        return response

    if job_id:
        job = SchedulerService.get_job(job_id)

        saved_job = await ScheduledJobService(uow).get(
            job_id=job_id, user_id=current_user.pk,
            prefetch_related=['user', 'team', 'app']
        )

        if not saved_job:
            raise NotFound("Saved scheduled job not found!")

        response.append(JobResponse(
            id=job.id,
            name=job.name,
            status=saved_job.status,
            next_run_time=job.next_run_time,
            trigger=format_trigger(job.trigger),
            app=saved_job.app.name,
            user=saved_job.user,
            team=saved_job.team,
        ))

        return response

    saved_jobs_dict = await ScheduledJobService(uow).get_scheduled_jobs_dict()

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
            JobResponse(
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

    return MisResponse[list[JobResponse]](result=response)


@router.post(
    '/add',
    response_model=MisResponse[JobResponse]
)
async def add_job(
        uow: UnitOfWorkDep,
        task_id: str,
        job_in: JobCreate = None,
        current_user: User = Depends(get_current_user),
):
    if job_in:
        extra = job_in.extra
        trigger = make_trigger(job_in.trigger) if job_in.trigger else None
    else:
        extra = None
        trigger = None

    if job_in and job_in.trigger:
        interval = job_in.trigger.interval
        cron = job_in.trigger.cron
    else:
        interval = None
        cron = None

    job = await SchedulerService.add_job(
        task_id=task_id, user=current_user, extra=extra, trigger=trigger)

    # add job to db
    job_db = await ScheduledJobService(uow).create_scheduled_job(
        job_id=job.id, user=current_user, extra=extra, interval=interval, cron=cron)
    job_db_with_related = await ScheduledJobService(uow).get(
        id=job_db.pk, prefetch_related=['app', 'user', 'team'])

    job_response = JobResponse(
        id=job.id,
        name=job.name,
        next_run_time=job.next_run_time,
        trigger=format_trigger(job.trigger),
        status=job_db_with_related.status,
        app=job_db_with_related.app.name,
        user=job_db_with_related.user,
        team=job_db_with_related.team,
    )

    return MisResponse[JobResponse](result=job_response)


@router.post(
    '/pause',
    response_model=MisResponse
)
async def pause_job(
        uow: UnitOfWorkDep,
        job_id: str,
        current_user: User = Depends(get_current_user)
):
    await SchedulerService.pause_job(job_id, current_user)
    await ScheduledJobService(uow).set_paused_status(job_id=job_id)

    return MisResponse()


@router.post(
    '/resume',
    response_model=MisResponse
)
async def resume_job(
        uow: UnitOfWorkDep,
        job_id: str,
        current_user: User = Depends(get_current_user)
):
    await SchedulerService.resume_job(job_id, current_user)
    await ScheduledJobService(uow).set_running_status(job_id=job_id)

    return MisResponse()


@router.post(
    '/reschedule',
    response_model=MisResponse
)
async def reschedule_job(
        uow: UnitOfWorkDep,
        job_id: str,
        schedule_in: JobScheduleUpdate,
):
    trigger = make_trigger(schedule_in)
    await SchedulerService.reschedule_job(job_id, trigger=trigger)

    await ScheduledJobService(uow).update_job_trigger(
        job_id=job_id,
        interval=schedule_in.interval,
        cron=schedule_in.cron,
    )
    return MisResponse()


@router.delete(
    '/remove',
    response_model=MisResponse
)
async def remove_job(
        uow: UnitOfWorkDep,
        job_id: str,
        current_user: User = Depends(get_current_user)
):
    await SchedulerService.remove_job(job_id, current_user)
    await ScheduledJobService(uow).delete(job_id=job_id, user_id=current_user.pk)

    return MisResponse()
