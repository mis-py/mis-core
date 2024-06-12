from fastapi import APIRouter
from core.utils.module.components import APIRoutes

from .dummy import router as dummy_router
from .dummy import restricted_router as dummy_restricted_router
from .mongo import router as mongo_router
from .redis import router as redis_router
from .websockets import router as websockets_router
from .groups import router as groups_router
from .elements import router as elements_router

router = APIRouter()
router.include_router(dummy_router, tags=["dummy"])
router.include_router(dummy_restricted_router, tags=["dummy-restricted"], prefix='/restricted')
router.include_router(mongo_router, tags=["mongo"], prefix='/mongo')
router.include_router(redis_router, tags=["redis"], prefix='/redis')
router.include_router(websockets_router, tags=["websockets"], prefix='/websockets')
router.include_router(groups_router, tags=["groups"], prefix='/groups')
router.include_router(elements_router, tags=["elements"], prefix='/elements')

api_router = APIRoutes(router)