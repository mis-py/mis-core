from typing import Optional, Annotated

import loguru
from fastapi import Security, APIRouter, Depends
from core.db.models import User
from core.dependencies.path import get_user_by_id, get_team_by_id
from core.dependencies.security import get_current_user
from core.dependencies.uow import UnitOfWorkDep
from core.exceptions import NotFound, AlreadyExists
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
        uow: UnitOfWorkDep,
        team_id: int = None,
):
    if team_id is not None:
        await get_team_by_id(uow=uow, team_id=team_id)

    return await UserService(uow).filter_and_paginate(
        team_id=team_id,
        prefetch_related=['settings', 'team']
    )


@router.get(
    '/my',
    response_model=MisResponse[UserResponse]
)
async def get_user_me(
        uow: UnitOfWorkDep,
        user: User = Depends(get_current_user)
):
    user_with_related = await UserService(uow).get(
        id=user.pk,
        prefetch_related=['team', 'settings']
    )

    return MisResponse[UserResponse](result=user_with_related)


@router.put(
    '/my',
    response_model=MisResponse[UserResponse]
)
async def edit_user_me(
        uow: UnitOfWorkDep,
        user_in: UserSelfUpdate,
        user: User = Depends(get_current_user),
):
    user_service = UserService(uow)
    await user_service.update(id=user.pk, schema_in=user_in)
    user_with_related = await user_service.get(
        id=user.pk, prefetch_related=['team', 'settings'])

    return MisResponse[UserResponse](result=user_with_related)


@router.post(
    '/add',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])],
    response_model=MisResponse[UserResponse]
)
async def create_user(uow: UnitOfWorkDep, user_in: UserCreate):
    # TODO rewrite it on dependency test
    user = await UserService(uow).get(username=user_in.username)

    if user:
        raise AlreadyExists(f"User with username '{user_in.username}' already exists")
    # # TODO here as well
    if user_in.team_id is not None:
        team = await TeamService(uow).get(id=user_in.team_id)
        if not team:
            raise NotFound(f"Team id '{user_in.team_id}' not exist")

    new_user = await UserService(uow).create_with_pass(user_in)
    new_user_with_related = await UserService(uow).get(
        id=new_user.pk, prefetch_related=['team', 'settings'])

    return MisResponse[UserResponse](result=new_user_with_related)


@router.get(
    '/get',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])],
    response_model=MisResponse[UserResponse]
)
async def get_user(
        uow: UnitOfWorkDep,
        user: User = Depends(get_user_by_id)
):
    user_with_related = await UserService(uow).get(
        id=user.pk, prefetch_related=['team', 'settings'])

    return MisResponse[UserResponse](result=user_with_related)


@router.put(
    '/edit',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])],
    response_model=MisResponse[UserResponse]
)
async def edit_user(
        uow: UnitOfWorkDep,
        user_in: UserUpdate,
        user: User = Depends(get_user_by_id),
):
    await UserService(uow).update_with_password(user, user_in)
    user_with_related = await UserService(uow).get(
        id=user.pk, prefetch_related=['team', 'settings'])

    return MisResponse[UserResponse](result=user_with_related)


@router.delete(
    '/remove',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])],
    response_model=MisResponse
)
async def delete_user(uow: UnitOfWorkDep, user: User = Depends(get_user_by_id)):
    await UserService(uow).delete(id=user.pk)

    return MisResponse()
