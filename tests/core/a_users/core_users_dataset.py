from fastapi import status

positive_get_users_dataset = [
    (
        {},
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
                        "id": 1,
                        "username": "admin",
                        "position": None,
                        "disabled": False,
                        "team": {
                            "id": 1,
                            "name": "Superusers"
                        }
                    }
                ]
            },
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
            "result": {
                "total": 1,
                "current": 1,
                "size": 50,
                "pages": 1,
                "items": [
                    {
                        "id": 1,
                        "username": "admin",
                        "position": None,
                        "disabled": False,
                        "team": {
                            "id": 1,
                            "name": "Superusers"
                        }
                    }
                ]
            },
            "status": True
        }
    )
]

negative_get_users_dataset = [
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
    )
]

positive_create_user_dataset = [
    (
        {
            "username": "Test1",
            "password": "qwerty",
            "team_id": 1,
            "position": "TEST USER",
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
                "team": {"id": 1, "name": "Superusers"}
            }
        }
    ),
    # test without team_id
    (
        {
            "username": "Test2",
            "password": "qwerty",
            "position": "TEST USER 2",
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
                "team": None,
            }
        }
    )
]

negative_create_user_dataset = [
    (
        {
            "username": "Test",
            "password": "qwerty",
            "team_id": 0,
            "position": "TEST USER",
        },
        {
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND,
            "msg": "NotFound",
            "result": "Team id '0' not exist"

        }
    ),(
        # User is created by positive test
        {
            "username": "Test1",
            "password": "qwerty",
            "team_id": 1,
            "position": "TEST USER",
        },
        {
            "status": False,
            "status_code": status.HTTP_409_CONFLICT,
            "msg": "AlreadyExists",
            "result": "User with username 'Test1' already exists"
        }
    ),
]

positive_get_user_dataset = [
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
                "team": {"id": 1, "name": "Superusers"},
            }
        }
    ),
    (
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
                "team": None,
            }
        }
    ),
]

negative_get_user_dataset = [
    (
        {
            "user_id": 9999
        },
        {
            "msg": "NotFound",
            "result": "User not found",
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND
        }
    ),(
        # wrong parameter name
        {
            "id": 1234
        },
        {
            "status_code": 422,
            "msg": "RequestValidationError",
            "result": [
                "Field required ('query', 'user_id')"
            ],
            "status": False
        }
    ),
]

positive_edit_user_dataset = [
    (
        # change username and position
        {
            "user_id": 2,
        },
        {
            "username": "test999",
            "team_id": 1,
            "password": "",
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
                "team": {"id": 1, "name": "Superusers"},
            }
        }
    ),
    (
        # change password
        {
            "user_id": 3,
        },
        {
            "username": "Test2",
            "team_id": 1,
            "password": "ytrewq",
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
                "team": {"id": 1, "name": "Superusers"},
            }
        }
    ),
    (
        # without any params edit
        {
            "user_id": 3,
        },
        {},
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "id": 3,
                "username": "Test2",
                "position": "TEST USER 2",
                "disabled": False,
                "team": {
                    "id": 1,
                    "name": "Superusers"
                }
            },
            "status": True
        }
    )
]

negative_edit_user_dataset = [
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
            "msg": "NotFound",
            "result": "User not found"
        }
    ),
    (
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
    ),
]

positive_remove_user_dataset = [
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

negative_remove_user_dataset = [
    (
        # not exist user
        {
            "user_id": 9999,
        },
        {
            "msg": "NotFound",
            "result": "User not found",
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
            "msg": "MISError",
            "result": "User with id '1' can't be deleted",
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
            "status_code": 422,
            "msg": "RequestValidationError",
            "result": [
                "Field required ('query', 'user_id')"
            ],
            "status": False
        }
    )
]

get_users_dataset = positive_get_users_dataset + negative_get_users_dataset
create_user_dataset = positive_create_user_dataset + negative_create_user_dataset
get_user_dataset = positive_get_user_dataset + negative_get_user_dataset
edit_user_dataset = positive_edit_user_dataset + negative_edit_user_dataset
remove_user_dataset = positive_remove_user_dataset + negative_remove_user_dataset
