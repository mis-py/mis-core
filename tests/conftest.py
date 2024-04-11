import pytest
from fastapi.testclient import TestClient
import logging
from main import app
from tortoise import Tortoise

# TODO on test we need override db settings - create database, remove database


@pytest.fixture(scope="session")
def get_mis_client():
    with TestClient(app) as client:
        yield client


async def init_db(db_url, create_db, schemas):
    """Initial database connection"""
    await Tortoise.init(
        db_url=db_url, modules={"models": ["models"]}, _create_db=create_db
    )
    if create_db:
        print(f"Database created! {db_url = }")
    if schemas:
        await Tortoise.generate_schemas()
        print("Success to generate schemas")


@pytest.fixture(scope="session", autouse=True)
async def init_database():
    await init_db()
    yield
    await Tortoise._drop_databases()
