from fastapi import APIRouter

from core.dependencies.misc import AppContextDep
from core.utils.schema import MisResponse

from modules.binom_companion.schemas.lead_record import LeadRecordModel
from ..service import LeadRecordService

router = APIRouter()


@router.post(
    '/lead',
    response_model=MisResponse
)
async def lead_endpoint(ctx: AppContextDep, new_lead: LeadRecordModel):
    await LeadRecordService().add_new_record(ctx=ctx, new_lead=new_lead)

    return MisResponse()

