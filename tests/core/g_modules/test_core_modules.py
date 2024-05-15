import pytest
import logging
from tests.utils import default_check, check_response
from .core_modules_dataset import (
    get_modules_dataset,
    init_module_dataset,
    shutdown_module_dataset,
    start_module_dataset,
    stop_module_dataset,
)

log = logging.getLogger(__name__)


@pytest.fixture
def client(get_mis_client):
    return get_mis_client


@pytest.mark.parametrize("params, expected", init_module_dataset)
def test_init_module(client, params, expected):
    response = client.post("/modules/init", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['id'])


@pytest.mark.parametrize("params,expected", start_module_dataset)
def test_start_module(client, params, expected):
    response = client.post("/modules/start", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['id'])


@pytest.mark.parametrize("params , expected", get_modules_dataset)
def test_get_modules(client, params, expected):
    response = client.get("/modules", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['id'])


@pytest.mark.parametrize("params, expected", stop_module_dataset)
def test_stop_module(client, params, expected):
    response = client.post("/modules/stop", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['id'])


@pytest.mark.parametrize("params,expected", shutdown_module_dataset)
def test_shutdown_module(client, params, expected):
    response = client.post("/modules/shutdown", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['id'])

