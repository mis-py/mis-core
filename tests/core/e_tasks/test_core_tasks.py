import pytest
import logging
from tests.utils import default_check, check_response
from .core_tasks_dataset import (
    get_tasks_dataset
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


@pytest.mark.parametrize("params, expected", get_tasks_dataset)
def test_get_tasks(client, params, expected):
    response = client.get("/tasks", params=params)
    assert default_check(response)
    assert check_response(response, expected)
