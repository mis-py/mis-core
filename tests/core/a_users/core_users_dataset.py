from fastapi import status

positive_create_user_data_set = [
    (
        {
            "username": "Test1",
            "password": "qwerty",
            "team_id": 1,
            "settings": [],
            "position": "TEST USER",
            "permissions": []
        },
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {
                "id": 2,
                "username": "Test1",
                "position": "TEST USER",
                "disabled": False,
                "signed_in": False,
                "team": {"id": 1, "name": "Superusers"},
                "settings": []
            }
        }
    ),
    (
        {
            "username": "Test2",
            "password": "qwerty",
            "team_id": 1,
            "settings": [],
            "position": "TEST USER 2",
            "permissions": []
        },
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {
                "id": 3,
                "username": "Test2",
                "position": "TEST USER 2",
                "disabled": False,
                "signed_in": False,
                "team": {"id": 1, "name": "Superusers"},
                "settings": []
            }
        }
    )
]

negative_create_user_data_set = [
    (
        {
            "username": "Test",
            "password": "qwerty",
            "team_id": 0,
            "settings": [],
            "position": "TEST USER",
            "permissions": []
        },
        {
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND,
            "msg": "NotFound: Team id '0' not exist",
            "result": None

        }
    ),(
        # User is created by positive test
        {
            "username": "Test1",
            "password": "qwerty",
            "team_id": 1,
            "settings": [],
            "position": "TEST USER",
            "permissions": []
        },
        {
            "status": False,
            "status_code": status.HTTP_409_CONFLICT,
            "msg": "AlreadyExists: User with username 'Test1' already exists",
            "result": None
        }
    ),
]

positive_get_user_data_set = [
    (
        {
            "user_id": 2
        },
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {
                "id": 2,
                "username": "Test1",
                "position": "TEST USER",
                "disabled": False,
                "signed_in": False,
                "team": {"id": 1, "name": "Superusers"},
                "settings": []
            }
        }
    ),(
        {
            "user_id": 3
        },
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {
                "id": 3,
                "username": "Test2",
                "position": "TEST USER 2",
                "disabled": False,
                "signed_in": False,
                "team": {"id": 1, "name": "Superusers"},
                "settings": []
            }
        }
    ),
]

negative_get_user_data_set = [
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
    ),(
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

positive_edit_user_data_set = [
    (
        # change username and position
        {
            "user_id": 2,
        },
        {
            "username": "test999",
            "team_id": 1,
            "new_password": "",
            "disabled": False,
            "position": "TEST USER 999"
        },
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {
                "id": 2,
                "username": "test999",
                "position": "TEST USER 999",
                "disabled": False,
                "signed_in": False,
                "team": {"id": 1, "name": "Superusers"},
                "settings": []
            }
        }
    ),(
        # change password
        {
            "user_id": 3,
        },
        {
            "username": "Test2",
            "team_id": 1,
            "new_password": "ytrewq",
            "disabled": False,
            "position": "TEST USER 2"
        },
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {
                "id": 3,
                "username": "Test2",
                "position": "TEST USER 2",
                "disabled": False,
                "signed_in": False,
                "team": {"id": 1, "name": "Superusers"},
                "settings": []
            }
        }
    ),
]

negative_edit_user_data_set = [
    (
        # Test not exist user edit
        {
            "user_id": 9999,
        },
        {
            "username": "Test2",
            "team_id": 1,
            "new_password": "",
            "disabled": False,
            "position": "TEST USER 2"
        },
        {
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND,
            "msg": "NotFound: User not found",
            "result": None
        }
    ),(
        # Not exist team
        {
            "user_id": 3,
        },
        {
            "username": "Test2",
            "team_id": 9999,
            "new_password": "",
            "disabled": False,
            "position": "TEST USER 2"
        },
        {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "msg": "IntegrityError",
            "result": "Server error happen. Our devs already fired for that. Anyway see server log for error details.",
            "status": False
        }
    ),(
        # Username and position field missing
        {
            "user_id": 3,
        },
        {
            "team_id": 1,
            "new_password": "",
            "disabled": False,
        },
        {
            'status_code': status.HTTP_422_UNPROCESSABLE_ENTITY,
            'msg': 'RequestValidationError',
            'result': [
                {
                    'type': 'missing',
                    'loc': ['body', 'username'],
                    'msg': 'Field required',
                    'input': {'team_id': 1, 'new_password': '', 'disabled': False},
                    'url': 'https://errors.pydantic.dev/2.4/v/missing'
                },
                {
                    'type': 'missing',
                    'loc': ['body', 'position'],
                    'msg': 'Field required',
                    'input': {'team_id': 1, 'new_password': '', 'disabled': False},
                    'url': 'https://errors.pydantic.dev/2.4/v/missing'
                }
            ],
            'status': False
        }
    ),
]

positive_remove_user_data_set = [
    (
        {
            "user_id": 2,
        },
        {
          "status_code": status.HTTP_200_OK,
          "msg": "Success",
          "result": {},
          "status": True
        }
    ),(
        {
            "user_id": 3,
        },
        {
          "status_code": status.HTTP_200_OK,
          "msg": "Success",
          "result": {},
          "status": True
        }
    ),
]

negative_remove_user_data_set = [
    (
        # not exist user
        {
            "user_id": 9999,
        },
        {
            "msg": "NotFound: User not found",
            "result": None,
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND
        }
    ),
    (
        # admin user remove check
        {
            "user_id": 1,
        },
        {
            "msg": "MISError: User with id '1' can't be deleted.",
            "result": None,
            "status": False,
            "status_code": status.HTTP_400_BAD_REQUEST
        }
    ),
    (
        # wrong param name
        {
            "user": 2,
        },
        {
            "msg": "RequestValidationError",
            "result": [
                {
                    'input': None,
                    'loc': ['query', 'user_id'],
                    'msg': 'Field required',
                    'type': 'missing',
                    'url': 'https://errors.pydantic.dev/2.4/v/missing'
                }
            ],
            "status": False,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
        }
    )
]