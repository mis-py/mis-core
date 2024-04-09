from loguru import logger

from fastapi import APIRouter, Depends, Security, Response

from core.db.models import User
from core.dependencies import get_current_user
from core.dependencies.misc import UnitOfWorkDep
from core.exceptions import NotFound, MISError
from core.services.scheduled_job import ScheduledJobService

from services.scheduler import SchedulerService

from core.schemas.task import JobResponse, JobScheduleUpdate, JobCreate
from core.utils.task import format_trigger

router = APIRouter(dependencies=[
    Security(get_current_user, scopes=['core:sudo', 'core:tasks']),
])


@router.get(
    '',
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
    Get existent jobs \n
    :param task_id: Return jobs from specific task_id, can not be used with other *_id \n
    :param user_id: Return jobs from specific user_id, can not be used with other *_id \n
    :param team_id: Return jobs from specific team_id, can not be used with other *_id \n
    :param job_id: Return job for specific job_id, can not be used with other *_id
    """
    response = []

    if sum(1 for item in [task_id, user_id, team_id, job_id] if item is not None) > 1:
        raise MISError("Specified more than one filter!")

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

        return MisResponse[list[JobResponse]](result=response)

    saved_jobs_dict = await ScheduledJobService(uow).get_scheduled_jobs_dict()

    for job in SchedulerService.get_jobs():

        saved_job = saved_jobs_dict.get(job.id)

        if not saved_job:
            logger.error("Job not in saved jobs!")
            logger.error(job)
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
    return response


@router.post('/add')
async def add_job(
        uow: UnitOfWorkDep,
        job_in: JobCreate = None,
        current_user: User = Depends(get_current_user),
):
    job_db = await ScheduledJobService(uow).create_scheduled_job(user=current_user, job_in=job_in)

    job_response = JobResponse(
        id=job_db.job_id,
        name=job_db.task_name,
        status=job_db.status,
        app_id=job_db.app.pk,
        user_id=job_db.user.pk if job_in.type == 'user' else None,
        team_id=job_db.team.pk if job_in.type == 'team' else None,
    )


@router.post('/pause')
async def pause_job(
        uow: UnitOfWorkDep,
        job_id: int,
        current_user: User = Depends(get_current_user)
):
    await ScheduledJobService(uow).set_paused_status(job_id=job_id)
    return Response(status_code=200)


@router.post('/resume')
async def resume_job(
        uow: UnitOfWorkDep,
        job_id: int,
        current_user: User = Depends(get_current_user)
):
    await ScheduledJobService(uow).set_running_status(job_id=job_id)
    return Response(status_code=200)


@router.post('/reschedule')
async def reschedule_job(
        uow: UnitOfWorkDep,
        job_id: int,
        schedule_in: JobScheduleUpdate,
):
    await ScheduledJobService(uow).update_job_trigger(
        job_id=job_id,
        schedule_in=schedule_in
    )

    return MisResponse()


@router.delete('/remove')
async def remove_job(
        uow: UnitOfWorkDep,
        job_id: int,
        current_user: User = Depends(get_current_user)
):
    await ScheduledJobService(uow).cancel_job(job_id=job_id)

    return MisResponse()
