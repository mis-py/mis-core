from typing import Annotated

from fastapi import APIRouter, Depends

from core.dependencies.module import get_userless_app_context
from core.utils.schema import MisResponse
from core.utils.app_context import AppContext

from modules.binom_companion.schemas.lead_record import LeadRecordIn
from ..service import LeadRecordService

router = APIRouter()


@router.post(
    '/lead',
    response_model=MisResponse
)
async def lead_endpoint(
        new_lead: LeadRecordIn,
        ctx: Annotated[AppContext, Depends(get_userless_app_context)]
):
    await LeadRecordService().add_new_record(ctx=ctx, new_lead=new_lead)

    return MisResponse()

