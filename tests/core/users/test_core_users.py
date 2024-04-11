import loguru
import pytest
import logging
from tests.utils import default_check, compare_json
from .core_users_dataset import request_data_set

log = logging.getLogger(__name__)


@pytest.fixture
def client(get_mis_client):
    return get_mis_client


# Check that mis contains at least 1 user
def test_get_users(client):
    response = client.get("/users")
    assert default_check(response)

    response_json = response.json()

    assert response_json['status']
    assert response_json['status_code'] == 200

    assert len(response_json['result']['items']) >= 1


class TestCreateGetRemoveUser:

    @pytest.mark.parametrize("request_data,expected", request_data_set)
    def test_create_user(self, client, request_data, expected):
        response = client.post("/users/add", json=request_data)
        from services.tortoise_manager.tortoise_manager import TortoiseManager
        loguru.logger.debug(TortoiseManager.get_d())
        assert default_check(response)

        log.info(response.json())

        response_json = response.json()

        assert response_json['status'] == expected['status']
        assert response_json['status_code'] == expected['status_code']

        # excluded to many fields
        #assert compare_json(request_data, new_user, ("id","password","disabled", "signed_in"))

        #TestCreateGetRemoveUser.user = new_user
#
#     def test_get_user(self, client):
#         response = client.get("/users/get", params=[{"user_id": TestCreateGetRemoveUser.user.id}])
#         assert default_check(response)
#
#         log.info(response.status_code)
#         log.info(response.json())
#
#         assert compare_json(TestCreateGetRemoveUser.user)




