from fastapi import APIRouter
# from .router import router as lead_router
# from .domains import router as domain_router
# from .geos import router as geos_router
# from .geos_proxy import router as geos_proxy
from .utils import router as utils
from .tracker_instance import router as tracker_instance
from .replacement_groups import router as replacement_group
from .proxy_domains import router as proxy_domains
from .replacement_history import router as replacement_history

router = APIRouter()
router.include_router(tracker_instance, tags=["tracker"], prefix='/tracker_instance')
router.include_router(replacement_group, tags=["replacement_group"], prefix='/replacement_group')
router.include_router(proxy_domains, tags=["proxy_domains"], prefix='/proxy_domains')
router.include_router(replacement_history, tags=["replacement_history"], prefix='/replacement_history')
# router.include_router(lead_router, tags=["lead"])
# router.include_router(domain_router, tags=["domains"])
# router.include_router(geos_router, tags=["geos"])
# router.include_router(geos_proxy, tags=["geos-proxy"])
