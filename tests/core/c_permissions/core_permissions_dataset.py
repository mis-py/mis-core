from fastapi import status

positive_get_permissions_dataset = [
    (
        {
            'status_code': status.HTTP_200_OK,
            'msg': 'Success',
            'result': {
                'total': 11, 'current': 1, 'size': 50, 'pages': 1,
                'items':
                    [
                        {'id': 1, 'scope': 'core:sudo', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 2, 'scope': 'core:users', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 3, 'scope': 'core:teams', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 4, 'scope': 'core:modules', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 5, 'scope': 'core:groups', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 6, 'scope': 'core:notifications', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 7, 'scope': 'core:logs', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 8, 'scope': 'core:tasks', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 9, 'scope': 'core:consumers', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 10, 'scope': 'core:permissions', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 11, 'scope': 'dummy:dummy', 'app': {'id': 2, 'name': 'dummy', 'enabled': False}},
                    ]
            },
            'status': True
        }
    ),
]

negative_get_permissions_dataset = []

positive_get_user_permissions_dataset = [
    (
        {
            "user_id": 1
        },
        {
            'status_code': status.HTTP_200_OK,
            'msg': 'Success',
            'result': {
                'total': 2, 'current': 1, 'size': 50, 'pages': 1,
                'items': [
                    {
                        'id': 1,
                        'permission': {
                            'id': 1,
                            'scope': 'core:sudo',
                            'app': {
                                'id': 1,
                                'name': 'core',
                                'enabled': True
                            }
                        },
                        'user': {
                            'id': 1,
                            'username': 'admin',
                            'position': None
                        },
                        'team': None
                    },
                    {
                        # TODO WHY ID=3?
                        "id": 3,
                        "permission": {
                            "id": 11,
                            "scope": "dummy:dummy",
                            "app": {
                                "id": 2,
                                "name": "dummy",
                                "enabled": False
                            }
                        },
                        "user": {
                            "id": 1,
                            "username": "admin",
                            "position": None
                        },
                        "team": None
                    }
                ]
            },
            'status': True}
    ),
]

negative_get_user_permissions_dataset = [
    (
        {
            "user_id": 9999
        },
        {
            "msg": "NotFound: User not found",
            "result": None,
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND
        }
    ),
    (
        # wrong parameter name
        {
            "id": 1234
        },
        {
            "msg": "RequestValidationError",
            "result": [
                {
                    "type": "missing",
                    "loc": ["query", "user_id"],
                    "msg": "Field required",
                    "input": None,
                    "url": "https://errors.pydantic.dev/2.4/v/missing"
                }
            ],
            "status": False,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
        }
    ),
]

positive_edit_user_permissions_dataset = [
    (
        {
            "user_id": 1,
        },
        [
            {
                "permission_id": 11,
                "granted": True
            }
        ],
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {}
        }
    )
]

negative_edit_user_permissions_dataset = [
    (
        # Not exist team
        {
            "user_id": 9999,

        },
        [
            {
                "permission_id": 1,
                "granted": True
            }
        ],
        {
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND,
            "msg": "NotFound: User not found",
            "result": None
        }
    ),(
        {
            "user_id": 1,
        },
        [
            {
                "permission_id": 0,
                "granted": True
            }
        ],
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {}
        }
    )
]

positive_get_team_permissions_dataset = [
    (
        {
            "team_id": 1
        },
        {
            'status_code': status.HTTP_200_OK,
            'msg': 'Success',
            'result':
                {
                    'total': 1, 'current': 1, 'size': 50, 'pages': 1,
                    'items': [
                        {
                            'id': 2,
                            'permission': {
                                'id': 1, 'scope': 'core:sudo', 'app': {'id': 1, 'name': 'core', 'enabled': True}
                            },
                            'user': None,
                            'team': {'id': 1, 'name': 'Superusers'},
                        }
                    ]
                },
            'status': True}
    ),
]

negative_get_team_permissions_dataset = [
    (
        {
            "team_id": 9999
        },
        {
            "msg": "NotFound: Team not found",
            "result": None,
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND
        }
    ),
    (
        # wrong parameter name
        {
            "id": 1234
        },
        {
            "msg": "RequestValidationError",
            "result": [
                {
                    "type": "missing",
                    "loc": ["query", "team_id"],
                    "msg": "Field required",
                    "input": None,
                    "url": "https://errors.pydantic.dev/2.4/v/missing"
                }
            ],
            "status": False,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
        }
    ),
]

positive_edit_team_permissions_dataset = [
    (
        {
            "team_id": 1,
        },
        [
            {
                "permission_id": 11,
                "granted": True
            }
        ],
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {}
        }
    )
]

negative_edit_team_permissions_dataset = [
    (
        # Not exist team
        {
            "team_id": 9999,

        },
        [
            {
                "permission_id": 1,
                "granted": True
            }
        ],
        {
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND,
            "msg": "NotFound: Team not found",
            "result": None
        }
    ),(
        {
            "team_id": 1,
        },
        [
            {
                "permission_id": 0,
                "granted": True
            }
        ],
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {}
        }
    )
]

get_permissions_dataset = positive_get_permissions_dataset + negative_get_permissions_dataset
get_user_permissions_dataset = positive_get_user_permissions_dataset + negative_get_user_permissions_dataset
edit_user_permissions_dataset = positive_edit_user_permissions_dataset + negative_edit_user_permissions_dataset
get_team_permissions_dataset = positive_get_team_permissions_dataset + negative_get_team_permissions_dataset
edit_team_permissions_dataset = positive_edit_team_permissions_dataset + negative_edit_team_permissions_dataset
