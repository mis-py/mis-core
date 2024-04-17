import pytest
import logging
from tests.utils import default_check, check_response
from .core_permissions_dataset import (
    get_permissions_dataset,
    get_user_permissions_dataset,
    edit_user_permissions_dataset,
    get_team_permissions_dataset,
    edit_team_permissions_dataset
)

log = logging.getLogger(__name__)


@pytest.fixture
def client(get_mis_client):
    return get_mis_client


@pytest.mark.parametrize("expected", get_permissions_dataset)
def test_get_permissions(client, expected):
    response = client.get("/permissions")
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, expected", get_user_permissions_dataset)
def test_get_user_permissions(client, params, expected):
    response = client.get("/permissions/get/user", params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, request_data, expected", edit_user_permissions_dataset)
def test_edit_user_permissions(client, params, request_data, expected):
    response = client.put("/permissions/edit/user", json=request_data, params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, expected", get_team_permissions_dataset)
def test_get_team_permissions(client, params, expected):
    response = client.get("/permissions/get/team",  params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, request_data, expected", edit_team_permissions_dataset)
def test_edit_team_permissions(client, params, request_data, expected):
    response = client.put("/permissions/edit/team", json=request_data, params=params)
    assert default_check(response)
    assert check_response(response, expected)
