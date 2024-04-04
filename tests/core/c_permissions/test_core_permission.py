import pytest
import logging
from tests.utils import default_check, compare_json
from .core_permissions_dataset import \
    positive_get_permissions_dataset, \
    positive_get_user_permissions_data_set, negative_get_user_permissions_data_set, \
    positive_edit_user_permissions_data_set, negative_edit_user_permissions_data_set, \
    positive_get_team_permissions_data_set, negative_get_team_permissions_data_set, \
    positive_edit_team_permissions_data_set, negative_edit_team_permissions_data_set


log = logging.getLogger(__name__)


@pytest.fixture
def client(get_mis_client):
    return get_mis_client


@pytest.mark.parametrize("expected", positive_get_permissions_dataset)
def test_get_permissions(client, expected):
    response = client.get("/permissions")
    assert default_check(response)

    response_json = response.json()

    assert response_json['status']
    assert response_json['status_code'] == 200

    assert len(response_json['result']['items']) >= 1

    assert compare_json(response_json, expected)


@pytest.mark.parametrize("params,expected", positive_get_user_permissions_data_set+negative_get_user_permissions_data_set)
def test_get_user_permissions(client, params, expected):
    response = client.get("/permissions/get/user", params=params)
    assert default_check(response)

    response_json = response.json()

    assert compare_json(response_json, expected)


@pytest.mark.parametrize("params, request_data, expected", positive_edit_user_permissions_data_set+negative_edit_user_permissions_data_set)
def test_edit_user_permissions(client, params, request_data, expected):
    response = client.put("/permissions/edit/user", json=request_data, params=params)
    assert default_check(response)

    response_json = response.json()

    log.info(response_json)

    assert compare_json(response_json, expected)


@pytest.mark.parametrize("params, expected", positive_get_team_permissions_data_set+negative_get_team_permissions_data_set)
def test_get_team_permissions(client, params, expected):
    response = client.get("/permissions/get/team",  params=params)
    assert default_check(response)

    response_json = response.json()

    assert compare_json(response_json, expected)


@pytest.mark.parametrize("params, request_data, expected", positive_edit_team_permissions_data_set+negative_edit_team_permissions_data_set)
def test_remove_permissions(client, params, request_data, expected):
    response = client.put("/permissions/edit/team", json=request_data, params=params)
    assert default_check(response)

    response_json = response.json()

    assert compare_json(response_json, expected)
