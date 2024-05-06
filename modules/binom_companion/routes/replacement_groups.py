import loguru
from fastapi import APIRouter

from core.utils.schema import PageResponse, MisResponse

from ..schemas.replacement_group import ReplacementGroupModel, ReplacementGroupCreateModel
from ..service import ReplacementGroupService

router = APIRouter()


@router.get(
    '',
    response_model=PageResponse[ReplacementGroupModel]
)
async def get_replacement_groups():
    return await ReplacementGroupService().filter_and_paginate(
        prefetch_related=[
            # 'tracker_instance',
            'replacement_history'
        ]
    )


@router.post(
    '/add',
    response_model=MisResponse[ReplacementGroupModel]
)
async def create_replacement_group(replacement_group_in: ReplacementGroupCreateModel):
    replacement_group = await ReplacementGroupService().create(replacement_group_in)

    # await replacement_group.fetch_related("tracker_instance")

    return MisResponse[ReplacementGroupModel](result=replacement_group)


