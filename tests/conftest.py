import pytest
from fastapi.testclient import TestClient
import logging
from main import app


@pytest.fixture(scope="session")
def get_mis_client():
    with TestClient(app) as client:
        yield client
