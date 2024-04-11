# import pytest
# import logging
# from tests.utils import default_check, compare_json
# from .core_variables_dataset import \
#     positive_create_team_data_set, negative_create_team_data_set, \
#     positive_get_team_data_set, negative_get_team_data_set, \
#     positive_edit_team_data_set, negative_edit_team_data_set, \
#     positive_remove_team_data_set, negative_remove_team_data_set


# log = logging.getLogger(__name__)
#
#
# @pytest.fixture
# def client(get_mis_client):
#     return get_mis_client

#
# def test_get_teams(client):
#     response = client.get("/teams")
#     assert default_check(response)
#
#     response_json = response.json()
#
#     assert response_json['status']
#     assert response_json['status_code'] == 200
#
#     assert len(response_json['result']['items']) >= 1
#
#
# @pytest.mark.parametrize("request_data,expected", positive_create_team_data_set + negative_create_team_data_set)
# def test_create_team(client, request_data, expected):
#     response = client.post("/teams/add", json=request_data)
#     assert default_check(response)
#
#     response_json = response.json()
#
#     assert compare_json(response_json, expected)
#
#
# @pytest.mark.parametrize("params, expected", positive_get_team_data_set + negative_get_team_data_set)
# def test_get_team(client, params, expected):
#     response = client.get("/teams/get", params=params)
#     assert default_check(response)
#
#     response_json = response.json()
#
#     assert compare_json(response_json, expected)
#
#
# @pytest.mark.parametrize("params, request_data, expected", positive_edit_team_data_set + negative_edit_team_data_set)
# def test_edit_team(client, params, request_data, expected):
#     response = client.put("/teams/edit", json=request_data, params=params)
#     assert default_check(response)
#
#     response_json = response.json()
#
#     assert compare_json(response_json, expected)
#
#
# @pytest.mark.parametrize("params, expected", positive_remove_team_data_set + negative_remove_team_data_set)
# def test_remove_team(client, params, expected):
#     response = client.delete("/teams/remove", params=params)
#     assert default_check(response)
#
#     response_json = response.json()
#
#     assert compare_json(response_json, expected)
#


