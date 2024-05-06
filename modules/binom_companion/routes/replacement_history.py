import loguru
from fastapi import APIRouter

from core.utils.schema import PageResponse

from ..schemas.replacement_history import ReplacementHistoryBaseModel
from ..service import ProxyDomainService

router = APIRouter()


@router.get(
    '',
    response_model=PageResponse[ReplacementHistoryBaseModel]
)
async def get_replacement_history():
    return await ProxyDomainService().get_history_domains(
        prefetch_related=['from_domains', 'to_domain', 'replacement_group']
    )
