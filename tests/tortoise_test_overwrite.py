from types import ModuleType
from typing import Iterable, Union

from tortoise import Tortoise, generate_config
from tortoise.exceptions import DBConnectionError, OperationalError
from tortoise.contrib import test
from yoyo import get_backend, read_migrations

from libs.tortoise_manager import TortoiseManager
from tests.config import log

def _run_yoyo_migrations(migration_paths: list[str]):
    backend = get_backend(TortoiseManager._db_url)
    for migration_path in migration_paths:
        migrations = read_migrations(migration_path)
        try:
            with backend.lock():
                log.debug(f"[TestInitDB] Applying migration for: {migration_path} [{migrations}]")
                backend.apply_migrations(backend.to_apply(migrations))
        except Exception as e:
            e_name = e.__class__.__name__
            log.error(f"[TestInitDB] Error during migration: {migration_path} {e_name} {e}")

async def init_db(config: dict, migration_paths: list[str]) -> None:
    # Placing init outside the try block since it doesn't
    # establish connections to the DB eagerly.
    await Tortoise.init(config)
    try:
        await Tortoise._drop_databases()
    except (DBConnectionError, OperationalError):  # pragma: nocoverage
        pass

    await Tortoise.init(config, _create_db=True)
    _run_yoyo_migrations(migration_paths)

def get_db_config(app_label: str, modules: Iterable[Union[str, ModuleType]]) -> dict:
    """
    DB Config factory, for use in testing.

    :param app_label: Label of the app (must be distinct for multiple apps).
    :param modules: List of modules to look for models in.
    """
    return generate_config(
        test._TORTOISE_TEST_DB,
        app_modules={app_label: modules},
        testing=True,
        connection_label='models',  # removed app_label and hardcoded 'models' because it hardcoded in tortoise TestCase
    )
