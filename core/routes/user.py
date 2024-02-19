from typing import Optional

from fastapi import Security, APIRouter, Depends


from core.db.models import User, Variable
from core.crud import user, variable_value
from core.dependencies import get_user_by_id, get_current_user
from core.dependencies.path import PaginationDep
from core.schemas.user import EditUserMe, CreateUserInput, EditUserInput, UserDetailModel, UserListModel

router = APIRouter()


@router.get(
    '',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])],
    response_model=list[UserListModel],
)
async def get_users(pagination: PaginationDep, team_id: Optional[int] = None):
    users_query = await user.query_get_multi(**pagination, team_id=team_id)
    return await UserListModel.from_queryset(users_query)


@router.get('/my', response_model=UserDetailModel)
async def get_user_me(
        user: User = Depends(get_current_user)
):
    return await UserDetailModel.from_tortoise_orm(user)


@router.put('/my', response_model=UserDetailModel)
async def edit_user_me(
        data: EditUserMe,
        user: User = Depends(get_current_user)
):
    user = await user.update(user, obj_in=data)
    return await UserDetailModel.from_tortoise_orm(user)


@router.post('/add', response_model=UserDetailModel,
             dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])])
async def create_user(user_data: CreateUserInput):
    new_user = await user.create(user_data)

    await new_user.set_permissions(user_data.permissions)

    for variable in user_data.settings:
        await variable_value.set_variable_value(
            await Variable.get(id=variable.setting_id),
            variable.new_value, user=new_user
        )
    return await UserDetailModel.from_tortoise_orm(new_user)


@router.get('/get', response_model=UserDetailModel,
            dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])])
async def get_user(
        user: User = Depends(get_user_by_id)
):
    return await UserDetailModel.from_tortoise_orm(user)


@router.put('/edit', response_model=UserDetailModel,
            dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])])
async def edit_user(
        user_data: EditUserInput,
        user: User = Depends(get_user_by_id),
):
    await user.update(user, user_data)
    return await UserDetailModel.from_tortoise_orm(user)


@router.delete('/remove', dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])])
async def delete_user(user: User = Depends(get_user_by_id)):
    await user.delete()
    return True
