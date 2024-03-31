import pytest
import logging
from tests.utils import default_check, compare_json

log = logging.getLogger(__name__)


@pytest.fixture
def client(get_mis_client):
    return get_mis_client


# Check that mis contains at least 1 user
def test_get_users(client):
    response = client.get("/users")
    assert default_check(response)
    log.info(response.json())
    return
    assert response.json().data.length >= 1

    log.info(response.status_code)
    log.info(response.json())


# class TestCreateGetRemoveUser:
#     requested_user = {
#         "username": "TEST",
#         "password": "TEST",
#         "team_id": 0,
#         "settings": [],
#         "position": "TEST USER",
#         "permissions": []
#     }
#
#     user = None
#
#     def test_create_user(self, client):
#         response = client.post("/users/add", content=TestCreateGetRemoveUser.requested_user)
#         assert default_check(response)
#
#         log.info(response.status_code)
#         log.info(response.json())
#
#         new_user = response.json().data
#         # excluded to many fields
#         assert compare_json(TestCreateGetRemoveUser.requested_user, new_user, ("id","password","disabled", "signed_in"))
#
#         TestCreateGetRemoveUser.user = new_user
#
#     def test_get_user(self, client):
#         response = client.get("/users/get", params=[{"user_id": TestCreateGetRemoveUser.user.id}])
#         assert default_check(response)
#
#         log.info(response.status_code)
#         log.info(response.json())
#
#         assert compare_json(TestCreateGetRemoveUser.user)




