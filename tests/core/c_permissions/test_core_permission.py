import pytest
import logging
from tests.utils import default_check, check_response
from .core_permissions_dataset import (
    get_permissions_dataset,
    get_granted_permissions_dataset,
    edit_granted_permissions_dataset,
)

log = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def client(get_mis_client):
    get_mis_client.post('/modules/init', params={
        "module_id": 2
    })
    get_mis_client.post('/modules/start', params={
        "module_id": 2
    })

    yield get_mis_client

    get_mis_client.post('/modules/stop', params={
        "module_id": 2
    })
    get_mis_client.post('/modules/shutdown', params={
        "module_id": 2
    })


@pytest.mark.parametrize("expected", get_permissions_dataset)
def test_get_permissions(client, expected):
    response = client.get("/permissions")
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, expected", get_granted_permissions_dataset)
def test_get_granted_permissions(client, params, expected):
    response = client.get("/permissions/granted", params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, request_data, expected", edit_granted_permissions_dataset)
def test_edit_granted_permissions(client, params, request_data, expected):
    response = client.put("/permissions/granted", json=request_data, params=params)
    assert default_check(response)
    assert check_response(response, expected)
