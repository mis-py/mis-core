
positive_get_tasks = [
    (
        {},
        {
            "status_code": 200,
            "msg": "Success",
            "result": [
                {
                    "id": "dummy:dummy_task",
                    "name": "dummy_task",
                    "type": "user",
                    "extra_typed": {},
                    "trigger": 5,
                    # "is_has_jobs": False,
                    # "is_available_add_job": True
                },
                {
                    "id": "dummy:dummy_manual_task",
                    "name": "dummy_manual_task",
                    "type": "user",
                    "extra_typed": {
                        "dummy_argument": "str"
                    },
                    "trigger": None,
                    # "is_has_jobs": False,
                    # "is_available_add_job": True
                },
                {
                    "id": "dummy:dummy_single_task",
                    "name": "dummy_single_task",
                    "type": "user",
                    "extra_typed": {},
                    "trigger": None,
                    # "is_has_jobs": False,
                    # "is_available_add_job": True
                }
            ],
            "status": True
        }
    ),
    (
        {
            "task_id": "dummy:dummy_task"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": [
                {
                    "id": "dummy:dummy_task",
                    "name": "dummy_task",
                    "type": "user",
                    "extra_typed": {},
                    "trigger": 5,
                    # "is_has_jobs": False,
                    # "is_available_add_job": True
                }
            ],
            "status": True
        }
    ),
    (
        {
            "task_id": "dummy:dummy_manual_task"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": [
                {
                    "id": "dummy:dummy_manual_task",
                    "name": "dummy_manual_task",
                    "type": "user",
                    "extra_typed": {
                        "dummy_argument": "str"
                    },
                    "trigger": None,
                    # "is_has_jobs": False,
                    # "is_available_add_job": True
                }
            ],
            "status": True
        }
    )
]

negative_get_tasks = [
    (
        {
            "task_id": "NOT_EXIST_TASK"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": [],
            "status": True
        }
    ),
]

get_tasks_dataset = positive_get_tasks + negative_get_tasks
