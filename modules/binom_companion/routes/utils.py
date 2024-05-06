import re
import urllib3
from fastapi import APIRouter, Response, Request
from loguru import logger

from core.dependencies.misc import RoutingKeysDep
from core.dependencies.variables import VariablesDep
from core.utils.notification.message import Message
from core.utils.notification.recipient import Recipient


from ..config import RoutingKeys

# from ..db.models import ChangedDomain
# from ..db.schemas import ChangedDomainModel
from modules.binom_companion.db.models import LeadRecord
from ..db.pydantic_models import Lead


router = APIRouter()


@router.get('/test')
async def test(variables: VariablesDep, routing_keys: RoutingKeysDep):
    return routing_keys.NEW_LEAD


@router.post('/lead')
async def lead_endpoint(request: Request, new_lead: Lead):
    # if new_lead.id is None:
    #     return Response(status_code=400)

    module_proxy = request.state.module_proxy

    #logger.debug(new_lead)

    # if not new_lead.us:  # skipping lead without tag
    #     logger.warning('Got lead without tag!')
    #     logger.warning(f' - new_lead.alter_id = {new_lead.id}')
    #     logger.warning(f' - {new_lead.country = }')
    #     logger.warning(f' - {new_lead.offer_id = }')
    #     logger.warning(f' - {new_lead.landing = }')
    #     return Response(status_code=200)

    if new_lead.us is not None and re.match('aff[0-9]+-[0-9]+', new_lead.us):
        new_lead.us, new_lead.landing = new_lead.us.split('-')

    # Android app campaign naming
    if new_lead.us is not None and re.match('^[A-Z]+_[A-Za-z0-9]+_[A-Za-z0-9]+_[A-Za-z0-9]+$', new_lead.us):
        new_lead.us, _, _, _ = new_lead.us.split('_')

    # Android app campaign naming
    if new_lead.us is not None and len(new_lead.us) > 10:
        new_lead.us = new_lead.us[:2]
        
    if not new_lead.us:
        logger.debug(f"Possible wrong utm source: {new_lead}")
        new_lead.us = ""

    url = urllib3.util.parse_url(new_lead.referer or new_lead.origin)
    new_lead.origin = url.host
    new_lead.referer = url.host

    await LeadRecord.create(domain=new_lead.referer, geo=new_lead.country, tag=new_lead.us)

    await module_proxy.publish_event(
        obj=Message(
            source_type=Message.Source.EXTRA,
            data_type=Message.Data.INFO,
            recipient=Recipient(user_id=1),
            body=new_lead.dict(),
        ),
        routing_key=routing_keys.NEW_LEAD,
    )
    return Response(status_code=200)

# @router.get('/history')
# async def get_history() -> list[ChangedDomainModel]:
#     return await ChangedDomain.all()
