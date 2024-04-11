from fastapi.testclient import TestClient
import logging
from main import app

log = logging.getLogger(__name__)

def test_read_main():
    with TestClient(app) as client:
        response = client.get("/users")
        log.info(response.status_code)
        log.info(response.text)
        assert response.status_code == 200
        #assert response.json() == {"msg": "Hello World"}

