import logging
import sys
import uvicorn
from loguru import logger
from contextlib import asynccontextmanager
from functools import lru_cache
# from log import setup_logger
import json

from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from starlette import status
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from const import DEV_ENVIRONMENT, ENVIRONMENT
from config import CoreSettings
from loaders import (
    init_core, init_modules, init_eventory, init_scheduler, init_core_routes,
    init_redis, init_migrations, pre_init_db, pre_init_modules, init_db, init_admin_user, init_mongo, init_guardian)
from loaders import (
    shutdown_modules, shutdown_eventory, shutdown_scheduler, shutdown_db, shutdown_redis, shutdown_mongo)
from core.exceptions import MISError, ErrorSchema
from core.utils.common import generate_unique_id, custom_log_timezone

logging.getLogger('uvicorn').handlers.clear()

logger.remove()
logger.configure(patcher=custom_log_timezone)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    # filter - process messages from specified module
    # filter="core"
)

# setup_logger('DEBUG', ignored=[
#     'aiosqlite.core', 'tortoise.backends', 'tortoise.utils',
#     'passlib', 'multipart', 'aiormq', 'aiogram.bot', 'aio_pika',
#     'selenium', 'PIL', 'google_auth_httplib2', 'googleapiclient',
# ])
# for name, level in {
#     'apscheduler': 'WARNING',
# }.items():
#     logging.getLogger(name).setLevel(level)


@lru_cache
def get_settings():
    return CoreSettings()


settings = get_settings()

origins = [
    "http://localhost:8080",
    "http://10.10.102.3:8080",
]


@asynccontextmanager
async def lifespan(application: FastAPI):
    await init_redis()
    await init_mongo()
    await init_eventory()
    await init_scheduler()

    # TODO why should we load settings to env??
    # await init_settings()

    await pre_init_db()
    await pre_init_modules(app)
    await init_db(application)
    await init_modules(application)
    await init_migrations()
    await init_core()
    await init_admin_user()
    await init_guardian()
    await init_core_routes(application)

    logger.success('MIS Project API started!')
    yield

    await shutdown_modules()
    await shutdown_scheduler()
    await shutdown_eventory()
    await shutdown_mongo()
    await shutdown_redis()
    await shutdown_db()

    logger.success('MIS Project API shutdown complete!')


docs_url, openapi_url = None, None

if ENVIRONMENT == DEV_ENVIRONMENT:
    docs_url = settings.URL_ROOT_PATH + '/docs'
    openapi_url = settings.URL_ROOT_PATH + '/openapi.json'

app = FastAPI(
    title='MIS Project API',
    version='0.2.0',
    lifespan=lifespan,
    root_path=settings.URL_ROOT_PATH,
    docs_url=docs_url,
    openapi_url=openapi_url,
    redoc_url=None,  # disable it completely
    redirect_slashes=False,
    generate_unique_id_function=generate_unique_id,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(PyInstrumentProfilerMiddleware)


async def analyze(request: Request, call_next):
    headers = dict(request.headers)
    if request.headers.get('user-agent') == 'testclient':
        for line in json.dumps(headers, indent=4, ensure_ascii=False).splitlines():
            logger.debug(line)

    return await call_next(request)

app.add_middleware(BaseHTTPMiddleware, dispatch=analyze)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_name = exc.__class__.__name__
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logger.warning(f"{request.method} {request.scope['path']}: {exc_name} - {exc_str}")
    logger.error(f"Body: {exc.body}")
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    error_schema = ErrorSchema(
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        type=exc_name,
        message=exc_str,
        data=exc.errors(),
    )
    return JSONResponse(
        content={"error": error_schema.model_dump()},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


@app.exception_handler(MISError)
async def mis_error_exception_handler(request: Request, exc: MISError):
    exc_name = exc.__class__.__name__
    logger.warning(f"{request.method} {request.scope['path']}: {exc_name} - {exc.message}")
    error_schema = ErrorSchema(
        status=exc.status_code,
        type=exc_name,
        message=exc.message,
        data=exc.data,
    )
    return JSONResponse(
        content={"error": error_schema.model_dump()},
        status_code=exc.status_code,
    )


@app.get('/')
async def root():
    return Response(status_code=200)


# for debugging
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, log_level='error')
