import pytest
import logging
from tests.utils import default_check, check_response
from .core_tasks_dataset import (
    get_tasks_dataset
)

log = logging.getLogger(__name__)


@pytest.fixture
def client(get_mis_client):
    return get_mis_client


@pytest.mark.parametrize("params, expected", get_tasks_dataset)
def test_get_tasks(client, params, expected):
    response = client.get("/tasks", params=params)
    assert default_check(response)
    assert check_response(response, expected)
