import pytest
import logging

from tests.proxy_registry.a_proxy.proxy_dataset import add_proxy_dataset, get_proxy_dataset, edit_proxy_dataset, \
    del_proxy_dataset, change_status_proxy_dataset, \
    positive_check_proxy_dataset
from tests.utils import default_check, check_response

log = logging.getLogger(__name__)


@pytest.fixture
def client(get_mis_client):
    get_mis_client.post('/modules/init', params={
        "module_name": 'proxy_registry'
    })
    get_mis_client.post('/modules/start', params={
        "module_name": 'proxy_registry'
    })

    yield get_mis_client

    get_mis_client.post('/modules/stop', params={
        "module_name": 'proxy_registry'
    })
    get_mis_client.post('/modules/shutdown', params={
        "module_name": 'proxy_registry'
    })


@pytest.mark.parametrize("request_data, expected", add_proxy_dataset)
def test_add_proxy(client, request_data, expected):
    response = client.post("/proxy_registry/proxies/add", json=request_data)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, expected", get_proxy_dataset)
def test_get_proxy(client, params, expected):
    response = client.get("/proxy_registry/proxies/get", params=params)
    assert default_check(response)
    assert check_response(response, expected)

# test commented because proxy can be not actual
# @pytest.mark.parametrize("request_data, expected", positive_check_proxy_dataset)
# def test_check_proxy(client, request_data, expected):
#     response = client.post("/proxy_registry/proxies/check", json=request_data)
#     assert default_check(response)
#     assert check_response(response, expected, ignore_keys=['text'])

def test_negative_check_proxy(client):
    response = client.post("/proxy_registry/proxies/check", json={'id': None, 'proxy_address': 'http://invalid.proxy'})
    assert default_check(response)
    assert response.json().get('result', {}).get('status') == 0


@pytest.mark.parametrize("params, request_data, expected", edit_proxy_dataset)
def test_edit_proxy(client, params, request_data, expected):
    response = client.put("/proxy_registry/proxies/edit", params=params, json=request_data)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, expected", change_status_proxy_dataset)
def test_change_status_proxy(client, params, expected):
    response = client.post("/proxy_registry/proxies/change-status", params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, expected", del_proxy_dataset)
def test_del_proxy(client, params, expected):
    response = client.delete("/proxy_registry/proxies/remove", params=params)
    assert default_check(response)
    assert check_response(response, expected)
