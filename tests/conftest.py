import pytest
from fastapi.testclient import TestClient
from main import app
from services.tortoise_manager import TortoiseManager
from tortoise import Tortoise, ConfigurationError, connections

import logging

log = logging.getLogger(__name__)

logging.getLogger('passlib').setLevel(logging.ERROR)


@pytest.fixture(scope="session")
def get_mis_client(init_database):
    log.info("Create app client")
    # maybe rework on full lifespan support for tests?
    # https://github.com/adriangb/misc/tree/starlette-state-lifespan
    with TestClient(app) as client:
        yield client
    pass


async def drop_databases():
    try:
        await Tortoise._drop_databases()
    except ConfigurationError:
        log.warning("[TortoiseManager] Database not initialized")


@pytest.fixture(scope="session")
async def init_database():
    log.info("Init Tortoise to cleanup before tests")
    # Call init() directly to init without create_db flag
    await Tortoise.init(
        db_url=TortoiseManager._db_url,
        modules=TortoiseManager._modules,
    )
    # await Tortoise.init(config=TortoiseManager._tortiose_orm)
    await drop_databases()
    await connections.close_all()

    yield

    log.info("Cleanup Tortoise after tests")
    await drop_databases()

