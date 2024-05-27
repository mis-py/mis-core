import loguru
from fastapi import APIRouter, Security

from core.dependencies.security import get_current_user
from core.utils.schema import PageResponse

from ..schemas.replacement_history import ReplacementHistoryModel
from ..service import ProxyDomainService

router = APIRouter(
    dependencies=[Security(get_current_user, scopes=[
        'binom_companion:sudo',
        'binom_companion:replacement_history'
    ])],
)


@router.get(
    '',
    response_model=PageResponse[ReplacementHistoryModel]
)
async def get_replacement_history():
    return await ProxyDomainService().get_history_domains(
        prefetch_related=[
            'from_domains', 'to_domain', 'replacement_group', 'replaced_by'
        ]
    )
