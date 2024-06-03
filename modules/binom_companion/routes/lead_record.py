from fastapi import APIRouter

from core.dependencies.misc import UserlessAppContextDep
from core.utils.schema import MisResponse

from modules.binom_companion.schemas.lead_record import LeadRecordIn
from ..service import LeadRecordService

router = APIRouter()


@router.post(
    '/lead',
    response_model=MisResponse
)
async def lead_endpoint(ctx: UserlessAppContextDep, new_lead: LeadRecordIn):
    await LeadRecordService().add_new_record(ctx=ctx, new_lead=new_lead)

    return MisResponse()

