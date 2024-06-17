from fastapi import status

# global only to global
# local only to local

positive_get_global_variables = [
    (
        {},
        {
            "status_code": 200,
            "msg": "Success",
            "result": [
                {
                    "id": 1,
                    "key": "TICK_N_SEC",
                    "default_value": "60",
                    "is_global": True,
                    "type": "int"
                },
                {
                    "id": 2,
                    "key": "LOG_LEVEL",
                    "default_value": "DEBUG",
                    "is_global": True,
                    "type": "str"
                },
                {
                    "id": 3,
                    "key": "PRIVATE_SETTING",
                    "default_value": "very private",
                    "is_global": False,
                    "type": "str"
                }
            ],
            "status": True
        }
    ),
    # test cases disabled due to is_global param disabled
    # (
    #     {
    #         "is_global": True
    #     },
    #     {
    #         "status_code": 200,
    #         "msg": "Success",
    #         "result": {
    #             "total": 2,
    #             "current": 1,
    #             "size": 50,
    #             "pages": 1,
    #             "items": [
    #                 {
    #                     "id": 1,
    #                     "key": "TICK_5_SEC",
    #                     "default_value": "5",
    #                     "is_global": True,
    #                     "type": "int"
    #                 },
    #                 {
    #                     "id": 2,
    #                     "key": "LOG_LEVEL",
    #                     "default_value": "DEBUG",
    #                     "is_global": True,
    #                     "type": "str"
    #                 }
    #             ]
    #         },
    #         "status": True
    #     }
    # ),
    # (
    #     {
    #         "is_global": False
    #     },
    #     {
    #         "status_code": 200,
    #         "msg": "Success",
    #         "result": {
    #             "total": 1,
    #             "current": 1,
    #             "size": 50,
    #             "pages": 1,
    #             "items": [
    #                 {
    #                     "id": 3,
    #                     "key": "PRIVATE_SETTING",
    #                     "default_value": "very private",
    #                     "is_global": False,
    #                     "type": "str"
    #                 }
    #             ]
    #         },
    #         "status": True
    #     }
    # ),
    # (
    #     # ID 1 is Core
    #     {
    #         "is_global": True,
    #         "module_id": 1,
    #     },
    #     {
    #         "status_code": 200,
    #         "msg": "Success",
    #         "result": {
    #             "total": 0,
    #             "current": 1,
    #             "size": 50,
    #             "pages": 0,
    #             "items": []
    #         },
    #         "status": True
    #     }
    # ),
    # (
    #     # ID 1 is Core
    #     {
    #         "is_global": False,
    #         "module_id": 1,
    #     },
    #     {
    #         "status_code": 200,
    #         "msg": "Success",
    #         "result": {
    #             "total": 0,
    #             "current": 1,
    #             "size": 50,
    #             "pages": 0,
    #             "items": []
    #         },
    #         "status": True
    #     }
    # ),
    # (
    #     {
    #         "is_global": True,
    #         "module_id": 2,
    #     },
    #     {
    #         "status_code": 200,
    #         "msg": "Success",
    #         "result": {
    #             "total": 2,
    #             "current": 1,
    #             "size": 50,
    #             "pages": 1,
    #             "items": [
    #                 {
    #                     "id": 1,
    #                     "key": "TICK_5_SEC",
    #                     "default_value": "5",
    #                     "is_global": True,
    #                     "type": "int"
    #                 },
    #                 {
    #                     "id": 2,
    #                     "key": "LOG_LEVEL",
    #                     "default_value": "DEBUG",
    #                     "is_global": True,
    #                     "type": "str"
    #                 }
    #             ]
    #         },
    #         "status": True
    #     }
    # ),
    # (
    #     {
    #         "is_global": False,
    #         "module_id": 2,
    #     },
    #     {
    #         "status_code": 200,
    #         "msg": "Success",
    #         "result": {
    #             "total": 1,
    #             "current": 1,
    #             "size": 50,
    #             "pages": 1,
    #             "items": [
    #                 {
    #                     "id": 3,
    #                     "key": "PRIVATE_SETTING",
    #                     "default_value": "very private",
    #                     "is_global": False,
    #                     "type": "str"
    #                 }
    #             ]
    #         },
    #         "status": True
    #     }
    # ),
    (
        # ID 1 is Core
        {
            "module_id": 1,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": [],
            "status": True
        }
    ),
    (
        {
            "module_name": "dummy",
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": [
                {
                    "id": 1,
                    "key": "TICK_N_SEC",
                    "default_value": "60",
                    "is_global": True,
                    "type": "int"
                },
                {
                    "id": 2,
                    "key": "LOG_LEVEL",
                    "default_value": "DEBUG",
                    "is_global": True,
                    "type": "str"
                },
                {
                    "id": 3,
                    "key": "PRIVATE_SETTING",
                    "default_value": "very private",
                    "is_global": False,
                    "type": "str"
                }
            ],
            "status": True
        }
    ),
]

negative_get_global_variables = [
    (
        {
            "module_id": 0,
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Module not found",
            "status": False
        }
    )
]

positive_get_local_variables = [
    (
        {
            "user_id": 1
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": [],
            "status": True
        }
    ),
    (
        {
            "team_id": 1
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": [],
            "status": True
        }
    ),
]

negative_get_local_variables = [
    (
        {
            "user_id": 9999
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "User not found",
            "status": False
        }
    ),
    (
        {
            "team_id": 9999
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Team not found",
            "status": False
        }
    ),
    (
        # TODO that case should rise filter error both used forbidden
        {
            "user_id": 9999,
            "team_id": 9999
        },
        {
            'msg': 'MISError',
            'result': 'Use only one filter',
            'status': False,
            'status_code': 400
        }
    )
]


positive_set_global_variables = [
    (
        {
            "module_id": 2
        },
        [
            {
                "variable_id": 1,
                "new_value": 999
            },
            {
                "variable_id": 2,
                "new_value": "TEST"
            }
        ],
        {
            'msg': 'Success',
            'result': {},
            'status': True,
            'status_code': 200
        }
    ),
]

negative_set_global_variables = [
    (
        # Core is not editable
        {
            "module_id": 1
        },
        [
            {
                "variable_id": 1,
                "new_value": "TEST"
            }
        ],
        {
            "status": False,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "msg": "ValidationFailed",
            "result": "Module ID '1' has no editable variables"
        }
    ),
    (
        # Module not exist
        {
            "module_id": 9999
        },
        [
            {
                "variable_id": 1,
                "new_value": "TEST"
            }
        ],
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Module not found",
            "status": False
        }
    ),
    (
        # TODO actually, variables can be updated without module_id ??
        {
            "id": 1234
        },
        [
            {
                "variable_id": 1,
                "new_value": "TEST"
            }
        ],
        {'msg': 'Success', 'result': {}, 'status': True, 'status_code': 200}
    ),
    (
        # Set wrong value type
        {
            "module_id": 2
        },
        [
            {
                "variable_id": 1,
                "new_value": "TEST"
            }
        ],
        {
            "status": False,
            "status_code": 422,
            "msg": "ValidationFailed",
            "result": "Can't convert value 'TEST' to 'int' for Variable with ID '1'"
        }
    ),
]

positive_set_local_variables = [
    (
        {
            "user_id": 1
        },
        [
            {
                "variable_id": 3,
                "new_value": "test"
            }
        ],
        {'msg': 'Success', 'result': {}, 'status': True, 'status_code': 200}
    ),
    (
        {
            "team_id": 1
        },
        [
            {
                "variable_id": 3,
                "new_value": "test"
            }
        ],
        {'msg': 'Success', 'result': {}, 'status': True, 'status_code': 200}
    ),
]

negative_set_local_variables = [
    (
        {
            "user_id": 1,
        },
        [
            {
                "variable_id": 0,
                "new_value": "TEST"
            }
        ],
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "VariableValue with ID '0' not exist",
            "status": False
        }
    ),
    (
        {
            "user_id": 9999,
        },
        [
            {
                "variable_id": 1,
                "new_value": "TEST"
            }
        ],
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "User not found",
            "status": False
        }
    ),
    (
        {
            "team_id": 1,
        },
        [
            {
                "variable_id": 0,
                "new_value": "TEST"
            }
        ],
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "VariableValue with ID '0' not exist",
            "status": False
        }
    ),
    (
        {
            "team_id": 9999,
        },
        [
            {
                "variable_id": 1,
                "new_value": "TEST"
            }
        ],
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Team not found",
            "status": False
        }
    ),
    (
        {},
        [],
        {'msg': 'MISError', 'result': 'Use only one filter', 'status': False, 'status_code': 400}
    )
]


get_global_variables_dataset = positive_get_global_variables + negative_get_global_variables
get_local_variables_dataset = positive_get_local_variables + negative_get_local_variables

set_global_variables_dataset = positive_set_global_variables + negative_set_global_variables
set_local_variables_dataset = positive_set_local_variables + negative_set_local_variables
