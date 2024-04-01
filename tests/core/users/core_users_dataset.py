from fastapi import status

request_data_set = [
    (
        {
            "username": "Test1",
            "password": "qwerty",
            "team_id": 0,
            "settings": [],
            "position": "TEST USER",
            "permissions": []
        },
        {
            # NotFound: Team id '0' not exist
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND,
        }
    ),
    (
        {
            "username": "Test2",
            "password": "qwerty",
            "team_id": 1,
            "settings": [],
            "position": "TEST USER",
            "permissions": []
        },
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
        }
    ),
    (
        {
            "username": "Test2",
            "password": "qwerty",
            "team_id": 1,
            "settings": [],
            "position": "TEST USER",
            "permissions": []
        },
        {
            # AlreadyExists: User with username 'Test1' already exists
            "status": False,
            "status_code": status.HTTP_409_CONFLICT,
        }
    ),
]
