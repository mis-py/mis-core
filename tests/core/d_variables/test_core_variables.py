import pytest
import logging
from tests.utils import default_check, compare_json, pretty_json
from .core_variables_dataset import (
    get_variables_dataset,
    set_app_variables_dataset,
    get_app_variables_dataset,
    set_user_variables_dataset,
    get_user_variables_dataset
)

log = logging.getLogger(__name__)


@pytest.fixture
def client(get_mis_client):
    return get_mis_client


@pytest.mark.parametrize("params, expected", get_variables_dataset)
def test_get_variables(client, params, expected):
    response = client.get("/variables", params=params)
    assert default_check(response)

    response_json = response.json()

    log.info(expected)
    log.info(pretty_json(response_json))

    assert response_json['status']
    assert response_json['status_code'] == 200

    assert compare_json(response_json, expected)

#
# @pytest.mark.parametrize("request_data,expected", set_app_variables_dataset)
# def test_set_app_variables(client, request_data, expected):
#     response = client.put("/variables/app", json=request_data)
#     assert default_check(response)
#
#     response_json = response.json()
#
#     log.info(expected)
#     log.info(pretty_json(response_json))
#
#     assert compare_json(response_json, expected)
#
#
# @pytest.mark.parametrize("params, expected", get_app_variables_dataset)
# def test_get_app_variables(client, params, expected):
#     response = client.get("/variables/app", params=params)
#     assert default_check(response)
#
#     response_json = response.json()
#
#     log.info(expected)
#     log.info(pretty_json(response_json))
#
#     assert compare_json(response_json, expected)
#
#
# @pytest.mark.parametrize("params, request_data, expected", set_user_variables_dataset)
# def test_set_user_variables(client, params, request_data, expected):
#     response = client.put("/variables/user", json=request_data, params=params)
#     assert default_check(response)
#
#     response_json = response.json()
#
#     log.info(expected)
#     log.info(pretty_json(response_json))
#
#     assert compare_json(response_json, expected)
#
#
# @pytest.mark.parametrize("params, expected", get_user_variables_dataset)
# def test_get_user_variables(client, params, expected):
#     response = client.get("/variables/user", params=params)
#     assert default_check(response)
#
#     response_json = response.json()
#
#     log.info(expected)
#     log.info(pretty_json(response_json))
#
#     assert compare_json(response_json, expected)
