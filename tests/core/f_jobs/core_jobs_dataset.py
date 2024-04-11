
positive_get_jobs = [
    (
        # No jobs initially
        {},
        {
          "status_code": 200,
          "msg": "Success",
          "result": [],
          "status": True
        }
    ),
]

negative_get_jobs = []


positive_add_job = [
    (
        {
            "task_id": "dummy:dummy_task",
            "extra": {},
            "trigger": {
                "interval": 60,
            },
            "type": "user"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "id": 1,
                "name": "dummy_task",
                "status": "running",
                "app_id": 2,
                "user_id": 1,
                "team_id": None
            },
            "status": True
        }
    ),
    (
        {
            "task_id": "dummy:dummy_task",
            "extra": {},
            "trigger": {
                "cron": "* * * * *"
            },
            "type": "user"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "id": 2,
                "name": "dummy_task",
                "status": "running",
                "app_id": 2,
                "user_id": 1,
                "team_id": None
            },
            "status": True
        }
    ),
    (
        {
            "task_id": "dummy:dummy_manual_task",
            "extra": {
                'dummy_argument': 'dummy1'
            },
            "trigger": {
                "cron": "* * * * *"
            },
            "type": "user"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "id": 3,
                "name": "dummy_manual_task",
                "status": "paused",
                "app_id": 2,
                "user_id": 1,
                "team_id": None
            },
            "status": True
        }
    ),

]

negative_add_job = [
    (
        {
            "task_id": "dummy:dummy_manual_task",
            "extra": {
                'dummy_argument': 'dummy2'
            },
            "trigger": {
                "cron": "* * * * *"
            },
            "type": "user"
        },
        {
            "status_code": 409,
            "msg": "AlreadyExists",
            "result": "Scheduled job already exists",
            "status": False
        }
    ),
]














get_jobs_dataset = positive_get_jobs + negative_get_jobs
add_job_dataset = positive_add_job + negative_add_job
pause_job_dataset = []
resume_job_dataset = []
reschedule_job_dataset = []
delete_job_dataset = []
