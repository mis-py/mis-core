from yoyo import get_backend, read_migrations
from tortoise import Tortoise, connections
from tortoise.exceptions import DoesNotExist, IntegrityError
from loguru import logger
from starlette.requests import Request
from starlette.responses import JSONResponse
from const import TIMEZONE, BASE_DIR
from .config import TortoiseSettings

settings = TortoiseSettings()


class TortoiseManager:
    _tortiose_orm: dict = {
        "connections": {
            "default": (
                f"postgres://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
                f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
                if all((
                    settings.POSTGRES_USER,
                    settings.POSTGRES_PASSWORD,
                    settings.POSTGRES_HOST,
                    settings.POSTGRES_PORT,
                    settings.POSTGRES_DB
                )) else
                "sqlite://db.sqlite3"
            )
        },
        "apps": {
            # models is module name
            "models": {
                "models": ["core.db.models", "core.db.mixin", "core.db.restricted", "core.db.guardian"],
                "default_connection": "default",
            },
        },
        "timezone": TIMEZONE,
    }
    _migrations_to_apply: list = [str(BASE_DIR / "core" / "migrations")]

    @classmethod
    async def add_models(cls, app: str, models: list[str]):
        cls._tortiose_orm['apps'][app] = dict(
            models=models,
            default_connection="default"
        )

    @classmethod
    async def add_migrations(cls, path):
        cls._migrations_to_apply.append(path)

    @classmethod
    async def pre_init(cls):
        Tortoise.init_models(cls._tortiose_orm['apps']['models']['models'], 'models')

    @classmethod
    async def init(cls, app, generate_schemas, add_exception_handlers):
        await Tortoise.init(config=cls._tortiose_orm)

        # TODO it should run only once on empty database, maybe out of MIS code
        if generate_schemas:
            logger.info("Tortoise-ORM generating schema")
            await Tortoise.generate_schemas()

        if add_exception_handlers:
            async def doesnotexist_exception_handler(request: Request, exc: DoesNotExist):
                return JSONResponse(status_code=404, content={"detail": str(exc)})

            app.add_exception_handler(DoesNotExist, doesnotexist_exception_handler)

            async def integrityerror_exception_handler(request: Request, exc: IntegrityError):
                return JSONResponse(
                    status_code=422,
                    content={"detail": [{"loc": [], "msg": str(exc), "type": "IntegrityError"}]},
                )

            app.add_exception_handler(IntegrityError, integrityerror_exception_handler)

    @classmethod
    async def init_migrations(cls):
        backend = get_backend(cls._tortiose_orm["connections"]["default"])
        migrations = read_migrations(*cls._migrations_to_apply)

        try:
            with backend.lock():
                backend.apply_migrations(backend.to_apply(migrations))
        except Exception as e:
            logger.error(f"[TortoiseManager] Error during migrations: {e}")

    @classmethod
    async def shutdown(cls):
        await connections.close_all()

