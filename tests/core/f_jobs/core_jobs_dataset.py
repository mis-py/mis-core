
positive_add_job = [
    (
        # use config defined trigger
        {
            "task_name": "dummy:dummy_task",
            "extra": {},
            "trigger": None,
            "type": "user"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "trigger": None,
                "job_id": 1,
                "name": "dummy_task",
                "task_name": "dummy_task",
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
            "task_name": "dummy:dummy_task",
            "extra": {},
            "trigger": 60,
            "type": "user"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "trigger": 60,
                "job_id": 2,
                "name": "dummy_task",
                "task_name": "dummy_task",
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
            "task_name": "dummy:dummy_task",
            "extra": {},
            "trigger": "* * * * *",
            "type": "user"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "trigger": "* * * * *",
                "job_id": 3,
                "name": "dummy_task",
                "task_name": "dummy_task",
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
            "task_name": "dummy:dummy_task",
            "extra": {},
            "trigger": ["* * * * *", "1 * * * *"],
            "type": "user"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "trigger": [
                    "* * * * *",
                    "1 * * * *"
                ],
                "job_id": 4,
                "name": "dummy_task",
                "task_name": "dummy_task",
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
            "task_name": "dummy:dummy_manual_task",
            "extra": {
                "dummy_argument": "dummy1",
                "dummy_second": 10,
                "dummy_kwarg": True,
            },
            "trigger": "* * * * *",
            "type": "user"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "trigger": "* * * * *",
                "job_id": 5,
                "name": "dummy_manual_task",
                "task_name": "dummy_manual_task",
                "status": "paused",
                "app_id": 2,
                "user_id": 1,
                "team_id": None
            },
            "status": True
        }
    ),
    (
        {
            "task_name": "dummy:dummy_single_task",
            "extra": {},
            "trigger": "* * * * *",
            "type": "user"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "trigger": "* * * * *",
                "job_id": 6,
                "name": "dummy_single_task",
                "task_name": "dummy_single_task",
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
        # not exist task check
        {
            "task_name": "dummy:dummy_task_not_exist",
            "extra": {},
            "trigger": None,
            "type": "user"
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Task 'dummy:dummy_task_not_exist' not exist",
            "status": False
        }
    ),
    (
        # team not yet supported check
        {
            "task_name": "dummy:dummy_task",
            "extra": {},
            "trigger": None,
            "type": "team"
        },
        {
            "status_code": 400,
            "msg": "MISError",
            "result": "Not supported yet",
            "status": False
        }
    ),
    (
        # single_instance task check
        {
            "task_name": "dummy:dummy_single_task",
            "extra": {},
            "trigger": "* * * * *",
            "type": "user"
        },
        {
            "status_code": 409,
            "msg": "AlreadyExists",
            "result": "Scheduled job already exists",
            "status": False
        }
    ),
    (
        # missing extra check
        {
            "task_name": "dummy:dummy_manual_task",
            "extra": {},
            "trigger": "* * * * *",
            "type": "user"
        },
        {
            "status_code": 422,
            "msg": "ValidationFailed",
            "result": "Requested extra params has incorrect values",
            "status": False
        }
    ),
    (
        # missing trigger check
        {
            "task_name": "dummy:dummy_manual_task",
            "extra": {
                'dummy_argument': 'dummy3'
            },
            "trigger": None,
            "type": "user"
        },
        {
            "status_code": 422,
            "msg": "ValidationFailed",
            "result": "Argument 'trigger' required for this task!",
            "status": False
        }
    )
]


positive_get_jobs = [
    (
        {},
        {
            "status_code": 200,
            "msg": "Success",
            "result": [
                {
                    "trigger": None,
                    "job_id": 1,
                    "name": "dummy_task",
                    "task_name": "dummy_task",
                    "status": "running",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                },
                {
                    "trigger": 60,
                    "job_id": 2,
                    "name": "dummy_task",
                    "task_name": "dummy_task",
                    "status": "running",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                },
                {
                    "trigger": "* * * * *",
                    "job_id": 3,
                    "name": "dummy_task",
                    "task_name": "dummy_task",
                    "status": "running",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                },
                {
                    "trigger": [
                        "* * * * *",
                        "1 * * * *"
                    ],
                    "job_id": 4,
                    "name": "dummy_task",
                    "task_name": "dummy_task",
                    "status": "running",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                },
                {
                    "trigger": "* * * * *",
                    "job_id": 5,
                    "name": "dummy_manual_task",
                    "task_name": "dummy_manual_task",
                    "status": "paused",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                },
                {
                    "trigger": "* * * * *",
                    "job_id": 6,
                    "name": "dummy_single_task",
                    "task_name": "dummy_single_task",
                    "status": "paused",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                }
            ],
            "status": True
        }
    ),
    (
        {
            "task_name": "dummy_task",
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": [
                {
                    "trigger": None,
                    "job_id": 1,
                    "name": "dummy_task",
                    "task_name": "dummy_task",
                    "status": "running",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                },
                {
                    "trigger": 60,
                    "job_id": 2,
                    "name": "dummy_task",
                    "task_name": "dummy_task",
                    "status": "running",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                },
                {
                    "trigger": "* * * * *",
                    "job_id": 3,
                    "name": "dummy_task",
                    "task_name": "dummy_task",
                    "status": "running",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                },
                {
                    "trigger": [
                        "* * * * *",
                        "1 * * * *"
                    ],
                    "job_id": 4,
                    "name": "dummy_task",
                    "task_name": "dummy_task",
                    "status": "running",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                }
            ],
            "status": True
        }
    ),
    (
        {
            "user_id": 1
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": [
                {
                    "trigger": None,
                    "job_id": 1,
                    "name": "dummy_task",
                    "task_name": "dummy_task",
                    "status": "running",
                    "app_id": 3,
                    "user_id": 1,
                    "team_id": None
                },
                {
                    "trigger": 60,
                    "job_id": 2,
                    "name": "dummy_task",
                    "task_name": "dummy_task",
                    "status": "running",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                },
                {
                    "trigger": "* * * * *",
                    "job_id": 3,
                    "name": "dummy_task",
                    "task_name": "dummy_task",
                    "status": "running",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                },
                {
                    "trigger": [
                        "* * * * *",
                        "1 * * * *"
                    ],
                    "job_id": 4,
                    "name": "dummy_task",
                    "task_name": "dummy_task",
                    "status": "running",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                },
                {
                    "trigger": "* * * * *",
                    "job_id": 5,
                    "name": "dummy_manual_task",
                    "task_name": "dummy_manual_task",
                    "status": "paused",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                },
                {
                    "trigger": "* * * * *",
                    "job_id": 6,
                    "name": "dummy_single_task",
                    "task_name": "dummy_single_task",
                    "status": "paused",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                }
            ],
            "status": True
        }
    ),
    (
        {
            "job_id": 2
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": [
                {
                    "trigger": 60,
                    "job_id": 2,
                    "name": "dummy_task",
                    "task_name": "dummy_task",
                    "status": "running",
                    "app_id": 2,
                    "user_id": 1,
                    "team_id": None
                }
            ],
            "status": True
        }
    )
]

negative_get_jobs = [
    (
        {
            "job_id": 2,
            "task_name": "dummy_task"
        },
        {
            "status_code": 400,
            "msg": "MISError",
            "result": "Specified more than one filter!",
            "status": False
        }
    )
]


positive_resume_job = [
    (
        {
            "job_id": 6,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "trigger": "* * * * *",
                "job_id": 6,
                "name": "dummy_single_task",
                "task_name": "dummy_single_task",
                "status": "running",
                "app_id": 2,
                "user_id": 1,
                "team_id": None
            },
            "status": True
        }
    ),
]

negative_resume_job = [
    (
        {
            "job_id": 12,
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Job ID '12' not found",
            "status": False
        }
    ),
]


positive_pause_job = [
    (
        {
            "job_id": 3
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "trigger": "* * * * *",
                "job_id": 3,
                "name": "dummy_task",
                "task_name": "dummy_task",
                "status": "paused",
                "app_id": 2,
                "user_id": 1,
                "team_id": None
            },
            "status": True
        }
    ),
    (
        {
            "job_id": 4
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "trigger": [
                    "* * * * *",
                    "1 * * * *"
                ],
                "job_id": 4,
                "name": "dummy_task",
                "task_name": "dummy_task",
                "status": "paused",
                "app_id": 2,
                "user_id": 1,
                "team_id": None
            },
            "status": True
        }
    ),
]

negative_pause_job = [
    (
        {
            "job_id": 12,
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Job ID '12' not found",
            "status": False
        }
    ),
]


positive_reschedule_job = [
    (
        {
            "job_id": 2,
        },
        {
            "trigger": 360
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "trigger": 360,
                "job_id": 2,
                "name": "dummy_task",
                "task_name": "dummy_task",
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
            "job_id": 5,
        },
        {
            "trigger": "1 1 * * *"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "trigger": "1 1 * * *",
                "job_id": 5,
                "name": "dummy_manual_task",
                "task_name": "dummy_manual_task",
                "status": "paused",
                "app_id": 2,
                "user_id": 1,
                "team_id": None
            },
            "status": True
        }
    ),
    (
        {
            "job_id": 6,
        },
        {
            "trigger": ["10 10 * * *", "20 20 * * *"]
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "trigger": [
                    "10 10 * * *",
                    "20 20 * * *"
                ],
                "job_id": 6,
                "name": "dummy_single_task",
                "task_name": "dummy_single_task",
                "status": "running",
                "app_id": 2,
                "user_id": 1,
                "team_id": None
            },
            "status": True
        }
    ),
    (
        # remove trigger, use task default
        {
            "job_id": 1,
        },
        {
            "trigger": None,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "trigger": None,
                "job_id": 1,
                "name": "dummy_task",
                "task_name": "dummy_task",
                "status": "running",
                "app_id": 2,
                "user_id": 1,
                "team_id": None
            },
            "status": True
        }
    ),
]

negative_reschedule_job = [
    (
        # no trigger
        {
            "job_id": 1,
        },
        {},
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "job_id": 1,
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
        # not exist job
        {
            "job_id": 12,
        },
        {
            "cron": ["* * * * *", "1 * * * *"]
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Job ID '12' not found",
            "status": False
        }
    ),
]


positive_delete_job = [
    (
        {
            "job_id": 1,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {},
            "status": True
        }
    ),
    (
        {
            "job_id": 2,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {},
            "status": True
        }
    ),
    (
        {
            "job_id": 3,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {},
            "status": True
        }
    ),
    (
        {
            "job_id": 4,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {},
            "status": True
        }
    ),
    (
        {
            "job_id": 5,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {},
            "status": True
        }
    ),
    (
        {
            "job_id": 6,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {},
            "status": True
        }
    ),
]

negative_delete_job = [
    (
        {
            "job_id": 1,
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Job ID '1' not found",
            "status": False
        }
    ),
    (
        {
            "job_id": 12,
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Job ID '12' not found",
            "status": False
        }
    ),
]


add_job_dataset = positive_add_job + negative_add_job
get_jobs_dataset = positive_get_jobs + negative_get_jobs
resume_job_dataset = positive_resume_job + negative_resume_job
pause_job_dataset = positive_pause_job + negative_pause_job
reschedule_job_dataset = positive_reschedule_job + negative_reschedule_job
delete_job_dataset = positive_delete_job + negative_delete_job
