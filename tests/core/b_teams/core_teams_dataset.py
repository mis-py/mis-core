from fastapi import status

positive_create_team_data_set = [
    (
        {
            "name": "Team1",
            "permissions": [],
            "users_ids": [],
            "variables": []
        },
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {
                'id': 2,
                'name': 'Team1',
                'permissions': [],
                'variables': [],
                'users': []
            }
        }
    ),(
        {
            "name": "Team2",
            "permissions": [],
            "users_ids": [],
            "variables": []
        },
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {
                'id': 3,
                'name': 'Team2',
                'permissions': [],
                'variables': [],
                'users': []
            }
        }
    ),
]

negative_create_team_data_set = [
    # (
    #     # in fact it create new team with id...
    #     {
    #         "name": "Team1",
    #         "permissions": [],
    #         "users_ids": [],
    #         "variables": []
    #     },
    #     {
    #         "status": True,
    #         "status_code": status.HTTP_200_OK,
    #         "msg": "Success",
    #         "result": {}
    #     }
    # )
]

positive_get_team_data_set = [
    (
        {
            "team_id": 2
        },
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {
                'id': 2,
                'name': 'Team1',
                'permissions': [],
                'variables': [],
                'users': []
            }
        }
    ),(
        {
            "team_id": 3
        },
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {
                'id': 3,
                'name': 'Team2',
                'permissions': [],
                'variables': [],
                'users': []
            }
        }
    ),
]

negative_get_team_data_set = [
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

positive_edit_team_data_set = [
    (
        {
            "team_id": 2,
        },
        {
            "name": "Team99",
            "permissions": [],
            "users_ids": [],
            "variables": []
        },
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {
                'id': 2,
                'name': 'Team99',
                'permissions': [],
                'variables': [],
                'users': []
            }
        }
    )
]

negative_edit_team_data_set = [
    (
        # Not exist team
        {
            "team_id": 9999,

        },
        {
            "name": "Team999",
            "permissions": [],
            "users_ids": [],
            "variables": []
        },
        {
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND,
            "msg": "NotFound: Team not found",
            "result": None
        }
    ),
    # (
    #     # Same team name
    #     {
    #         "team_id": 2,
    #     },
    #     {
    #         "name": "Team2",
    #         "permissions": [],
    #         "users_ids": [],
    #         "variables": []
    #     },
    #     {
    #         "status_code": status.HTTP_200_OK,
    #         "msg": "Success",
    #         "result": {},
    #         "status": True
    #     }
    # )
]

positive_remove_team_data_set = [
    (
        {
            "team_id": 2,
        },
        {
          "status_code": status.HTTP_200_OK,
          "msg": "Success",
          "result": {},
          "status": True
        }
    ),(
        {
            "team_id": 3,
        },
        {
          "status_code": status.HTTP_200_OK,
          "msg": "Success",
          "result": {},
          "status": True
        }
    ),
]

negative_remove_team_data_set = [
    (
        # not exist team
        {
            "team_id": 9999,
        },
        {
            "msg": "NotFound: Team not found",
            "result": None,
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND
        }
    ),
    (
        {
            "team_id": 1,
        },
        {
            "msg": "MISError: Team with id '1' can't be deleted.",
            "result": None,
            "status": False,
            "status_code": status.HTTP_400_BAD_REQUEST
        }
    ),
    (
        # wrong param name
        {
            "team": 2,
        },
        {
            "msg": "RequestValidationError",
            "result": [
                {
                    'input': None,
                    'loc': ['query', 'team_id'],
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