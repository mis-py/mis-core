from fastapi import status

positive_get_variables_dataset = [
    (
        {},
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "total": 3,
                "current": 1,
                "size": 50,
                "pages": 1,
                "items": [
                    {
                        "id": 1,
                        "key": "TICK_5_SEC",
                        "default_value": "5",
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
                ]
            },
            "status": True
        }
    ),
    (
        {
            "is_global": True
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "total": 2,
                "current": 1,
                "size": 50,
                "pages": 1,
                "items": [
                    {
                        "id": 1,
                        "key": "TICK_5_SEC",
                        "default_value": "5",
                        "is_global": True,
                        "type": "int"
                    },
                    {
                        "id": 2,
                        "key": "LOG_LEVEL",
                        "default_value": "DEBUG",
                        "is_global": True,
                        "type": "str"
                    }
                ]
            },
            "status": True
        }
    ),
    (
        {
            "is_global": False
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "total": 1,
                "current": 1,
                "size": 50,
                "pages": 1,
                "items": [
                    {
                        "id": 3,
                        "key": "PRIVATE_SETTING",
                        "default_value": "very private",
                        "is_global": False,
                        "type": "str"
                    }
                ]
            },
            "status": True
        }
    ),
    (
        # ID 1 is Core
        {
            "is_global": True,
            "module_id": 1,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "total": 0,
                "current": 1,
                "size": 50,
                "pages": 0,
                "items": []
            },
            "status": True
        }
    ),
    (
        # ID 1 is Core
        {
            "is_global": False,
            "module_id": 1,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "total": 0,
                "current": 1,
                "size": 50,
                "pages": 0,
                "items": []
            },
            "status": True
        }
    ),
    (
        {
            "is_global": True,
            "module_id": 2,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "total": 2,
                "current": 1,
                "size": 50,
                "pages": 1,
                "items": [
                    {
                        "id": 1,
                        "key": "TICK_5_SEC",
                        "default_value": "5",
                        "is_global": True,
                        "type": "int"
                    },
                    {
                        "id": 2,
                        "key": "LOG_LEVEL",
                        "default_value": "DEBUG",
                        "is_global": True,
                        "type": "str"
                    }
                ]
            },
            "status": True
        }
    ),
    (
        {
            "is_global": False,
            "module_id": 2,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "total": 1,
                "current": 1,
                "size": 50,
                "pages": 1,
                "items": [
                    {
                        "id": 3,
                        "key": "PRIVATE_SETTING",
                        "default_value": "very private",
                        "is_global": False,
                        "type": "str"
                    }
                ]
            },
            "status": True
        }
    ),
    (
        # ID 1 is Core
        {
            "module_id": 1,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "total": 0,
                "current": 1,
                "size": 50,
                "pages": 0,
                "items": []
            },
            "status": True
        }
    ),
    (
        {
            "module_id": 2,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "total": 3,
                "current": 1,
                "size": 50,
                "pages": 1,
                "items": [
                    {
                        "id": 1,
                        "key": "TICK_5_SEC",
                        "default_value": "5",
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
                ]
            },
            "status": True
        }
    ),
]

negative_get_variables_dataset = [
    (
        {
            "module_id": 0,
        },
        {
            "status_code": 404,
            "msg": "NotFound: Module not found",
            "result": None,
            "status": False
        }
    ),
]


positive_set_app_variables_dataset = [
    (
        {
            "module_id": 1
        },
        [
            {
                "setting_id": 1,
                "new_value": "TEST"
            }
        ],
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {}
        }
    ),
    (
        {
            "module_id": 2
        },
        [
            {
                "setting_id": 1,
                "new_value": "TEST"
            }
        ],
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {}
        }
    ),
]

negative_set_app_variables_dataset = [
    (
        {
            "module_id": 9999
        },
        {}
    ),
    (
        {
            "id": 1234
        },
        {}
    ),
    (
        # set variable to wrong module
        {
            "module_id": 1
        },
        [
            {
                "setting_id": 2,
                "new_value": "TEST"
            }
        ],
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {}
        }
    ),

]

positive_get_app_variables_dataset = [
    (
        {
            "module_id": 1
        },
        {}
    ),
    (
        {
            "module_id": 2
        },
        {}
    )
]

negative_get_app_variables_dataset = [
    (
        {
            "module_id": 9999
        },
        {}
    ),
    (
        {
            "id": 1234
        },
        {}
    ),
]


positive_set_user_variables_dataset = [
    (
        {
            "user_id": 1
        },
        [
          {
            "setting_id": 1,
            "new_value": "TEST"
          }
        ],
        {}
    ),
]

negative_set_user_variables_dataset = []

positive_get_user_variables_dataset = [
    (
        {
            "user_id": 1
        },
        {}
    ),
]

negative_get_user_variables_dataset = []


positive_set_team_variables_dataset = [
(
        {
            "team_id": 1
        },
        [
          {
            "setting_id": 1,
            "new_value": "TEST"
          }
        ],
        {}
    ),
]

negative_set_team_variables_dataset = []

positive_get_team_variables_dataset = [
    (
        {
            "team_id": 1
        },
        {}
    ),
]

negative_get_team_variables_dataset = []


get_variables_dataset = positive_get_variables_dataset + negative_get_variables_dataset
set_app_variables_dataset = positive_set_app_variables_dataset + negative_set_app_variables_dataset
get_app_variables_dataset = positive_get_app_variables_dataset + negative_get_app_variables_dataset
set_user_variables_dataset = positive_set_user_variables_dataset + negative_set_user_variables_dataset
get_user_variables_dataset = positive_get_user_variables_dataset + negative_get_user_variables_dataset
set_team_variables_dataset = positive_set_team_variables_dataset + negative_set_team_variables_dataset
get_team_variables_dataset = positive_get_team_variables_dataset + negative_get_team_variables_dataset
