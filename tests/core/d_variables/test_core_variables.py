import pytest
import logging
from tests.utils import default_check, check_response
from .core_variables_dataset import (
    get_global_variables_dataset,
    get_local_variables_dataset,
    set_global_variables_dataset,
    set_local_variables_dataset

)

log = logging.getLogger(__name__)


@pytest.fixture
def client(get_mis_client):
    return get_mis_client


@pytest.mark.parametrize("params, expected", get_global_variables_dataset)
def test_get_global_variables(client, params, expected):
    response = client.get("/variables/global", params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, expected", get_local_variables_dataset)
def test_get_local_variables(client, params, expected):
    response = client.get("/variables/local", params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, request_data,expected", set_global_variables_dataset)
def test_set_global_variables(client, params, request_data, expected):
    response = client.put("/variables/global", json=request_data, params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, request_data,expected", set_local_variables_dataset)
def test_set_local_variables(client, params, request_data, expected):
    response = client.put("/variables/local", json=request_data, params=params)
    assert default_check(response)
    assert check_response(response, expected)
