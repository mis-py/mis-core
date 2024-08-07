from typing import Optional, Annotated

from fastapi import Security, APIRouter, Depends
from core.db.models import User
from core.dependencies.path import get_user_by_id
from core.dependencies.security import get_current_user
from core.dependencies.services import get_user_service, get_team_service
from core.exceptions import AlreadyExists, NotFound
from core.schemas.user import UserResponse, UserUpdate, UserCreate, UserSelfUpdate, UserListResponse
from core.services.team import TeamService
from core.services.user import UserService
from core.utils.schema import MisResponse, PageResponse

router = APIRouter()


@router.get(
    '',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])],
    response_model=PageResponse[UserListResponse]
)
async def get_users(
        user_service: Annotated[UserService, Depends(get_user_service)],
        team_service: Annotated[TeamService, Depends(get_team_service)],
        team_id: Optional[int] = None,
):
    if team_id is not None:
        await team_service.get_or_raise(id=team_id)

    return await user_service.filter_and_paginate(
        team_id=team_id,
        prefetch_related=['variable_values', 'team']
    )


@router.get(
    '/my',
    response_model=MisResponse[UserResponse]
)
async def get_user_me(
        user_service: Annotated[UserService, Depends(get_user_service)],
        user: User = Depends(get_current_user)
):
    user_with_related = await user_service.get(
        id=user.pk,
        prefetch_related=['team', 'variable_values']
    )

    return MisResponse[UserResponse](result=user_with_related)


@router.put(
    '/my',
    response_model=MisResponse[UserResponse]
)
async def edit_user_me(
        user_service: Annotated[UserService, Depends(get_user_service)],
        user_in: UserSelfUpdate,
        user: User = Depends(get_current_user),
):
    await user_service.update_user(id=user.pk, schema_in=user_in)
    user_with_related = await user_service.get(
        id=user.pk, prefetch_related=['team', 'variable_values'])

    return MisResponse[UserResponse](result=user_with_related)


@router.post(
    '/add',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])],
    response_model=MisResponse[UserResponse]
)
async def create_user(
        user_service: Annotated[UserService, Depends(get_user_service)],
        user_in: UserCreate
):
    new_user = await user_service.create_with_pass(user_in)
    new_user_with_related = await user_service.get(
        id=new_user.pk, prefetch_related=['team', 'variable_values'])

    return MisResponse[UserResponse](result=new_user_with_related)


@router.get(
    '/get',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])],
    response_model=MisResponse[UserResponse]
)
async def get_user(
        user_service: Annotated[UserService, Depends(get_user_service)],
        user: User = Depends(get_user_by_id)
):
    user_with_related = await user_service.get(
        id=user.pk, prefetch_related=['team', 'variable_values'])

    return MisResponse[UserResponse](result=user_with_related)


@router.put(
    '/edit',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])],
    response_model=MisResponse[UserResponse]
)
async def edit_user(
        user_service: Annotated[UserService, Depends(get_user_service)],
        user_in: UserUpdate,
        user: User = Depends(get_user_by_id),
):
    await user_service.update_with_password(user, user_in)
    user_with_related = await user_service.get(
        id=user.pk, prefetch_related=['team', 'variable_values'])

    return MisResponse[UserResponse](result=user_with_related)


@router.delete(
    '/remove',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])],
    response_model=MisResponse
)
async def delete_user(
        user_service: Annotated[UserService, Depends(get_user_service)],
        user: User = Depends(get_user_by_id)):
    await user_service.delete(id=user.pk)

    return MisResponse()


@router.put(
    '/edit/user_data',
    response_model=MisResponse[dict]
)
async def edit_user_data(
        user_service: Annotated[UserService, Depends(get_user_service)],
        user_data: dict,
        user: User = Depends(get_user_by_id),
):
    saved_data = await user_service.update_user_data(
        id=user.pk,
        old_user_data=user.user_data,
        new_user_data=user_data,
    )
    return MisResponse[dict](result=saved_data)
