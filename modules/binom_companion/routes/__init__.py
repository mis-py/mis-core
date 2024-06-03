from fastapi import APIRouter

from .lead_record import router as lead_record
from .tracker_instance import router as tracker_instance
from .replacement_group import router as replacement_group
from .proxy_domain import router as proxy_domains
from .replacement_history import router as replacement_history

router = APIRouter()
router.include_router(tracker_instance, tags=["tracker"], prefix='/tracker_instance')
router.include_router(replacement_group, tags=["replacement_group"], prefix='/replacement_group')
router.include_router(proxy_domains, tags=["proxy_domains"], prefix='/proxy_domains')
router.include_router(replacement_history, tags=["replacement_history"], prefix='/replacement_history')
router.include_router(lead_record, tags=["lead_record"])
