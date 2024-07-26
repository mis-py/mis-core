
positive_get_tasks = [
    (
        {},
        {
            "status_code": 200,
            "msg": "Success",
            "result": [
                {
                    "trigger": 60,
                    "id": "dummy:dummy_task",
                    "name": "dummy_task",
                    "type": "user",
                    "extra_typed": {}
                },
                {
                    "trigger": None,
                    "id": "dummy:dummy_manual_task",
                    "name": "dummy_manual_task",
                    "type": "user",
                    "extra_typed": {
                        "dummy_argument": "str",
                        "dummy_second": "int",
                        "dummy_kwarg": "bool"
                    }
                },
                {
                    "trigger": None,
                    "id": "dummy:dummy_single_task",
                    "name": "dummy_single_task",
                    "type": "user",
                    "extra_typed": {}
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
                    "trigger": 60,
                    "id": "dummy:dummy_task",
                    "name": "dummy_task",
                    "type": "user",
                    "extra_typed": {}
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
                    "trigger": None,
                    "id": "dummy:dummy_manual_task",
                    "name": "dummy_manual_task",
                    "type": "user",
                    "extra_typed": {
                        "dummy_argument": "str",
                        "dummy_second": "int",
                        "dummy_kwarg": "bool"
                    }
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
