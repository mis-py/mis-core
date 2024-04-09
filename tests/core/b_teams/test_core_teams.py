import pytest
import logging
from tests.utils import default_check, check_response
from .core_teams_dataset import (
    get_teams_dataset,
    create_team_dataset,
    get_team_dataset,
    edit_team_dataset,
    remove_team_dataset
)


log = logging.getLogger(__name__)


@pytest.fixture
def client(get_mis_client):
    return get_mis_client


@pytest.mark.parametrize("expected", get_teams_dataset)
def test_get_teams(client, expected):
    response = client.get("/teams")
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("request_data,expected", create_team_dataset)
def test_create_team(client, request_data, expected):
    response = client.post("/teams/add", json=request_data)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, expected", get_team_dataset)
def test_get_team(client, params, expected):
    response = client.get("/teams/get", params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, request_data, expected", edit_team_dataset)
def test_edit_team(client, params, request_data, expected):
    response = client.put("/teams/edit", json=request_data, params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, expected", remove_team_dataset)
def test_remove_team(client, params, expected):
    response = client.delete("/teams/remove", params=params)
    assert default_check(response)
    assert check_response(response, expected)



