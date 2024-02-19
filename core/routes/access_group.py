from typing import Optional
from fastapi import Security, Depends, APIRouter, Response

from core.db.restricted import AccessGroup
from core.crud import access_group, restricted_object
from core.dependencies import get_current_user
from core.dependencies.path import PaginationDep, get_user_by_id

from core.dependencies.access_group import get_group_by_id
from core.schemas.access_group import CreateAccessGroup, ReadAccessGroup, ReadRestrictedObject

router = APIRouter(dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:access_groups'])])


@router.get('', response_model=list[ReadAccessGroup])
async def get_groups_list(pagination: PaginationDep, app_id: int = None, user_id: int = None):
    if user_id:
        user = await get_user_by_id(user_id)
        return await ReadAccessGroup.from_queryset(user.groups.all())

    groups_query = await access_group.query_get_multi(**pagination, app_id=app_id)
    return await ReadAccessGroup.from_queryset(groups_query)


@router.post('/add', response_model=ReadAccessGroup)
async def add_group(group_data: CreateAccessGroup):
    group = await access_group.create_with_users(name=group_data.name, users_ids=group_data.users_ids)
    return await ReadAccessGroup.from_tortoise_orm(group)


@router.get('/get', response_model=ReadAccessGroup)
async def get_group(group: AccessGroup = Depends(get_group_by_id)):
    return await ReadAccessGroup.from_tortoise_orm(group)


@router.put('/edit', response_model=ReadAccessGroup)
async def edit_group(group_data: CreateAccessGroup, group: AccessGroup = Depends(get_group_by_id)):
    if group_data.name:
        group.name = group_data.name

    # TODO edit group users here
    await group.save()

    return await ReadAccessGroup.from_tortoise_orm(group)


@router.delete('/remove')
async def delete_group(group: AccessGroup = Depends(get_group_by_id)):
    await access_group.remove(id=group.id)
    return Response(status_code=204)


# @router.get('/get/users', response_model=list[UserModelShort])
# async def get_group_users(group: UserGroup = Depends(get_group_by_id)):
#     users = await access_group.get_users(group=group)
#     return await UserModelShort.from_queryset(users)


# @router.put('/edit/users')
# async def set_group_users(users_ids: list[int], group: UserGroup = Depends(get_group_by_id)):
#     await access_group.set_group_users(group=group, users_ids=users_ids)
#     return Response(status_code=200)


@router.get('/objects', response_model=list[ReadRestrictedObject])
async def get_restricted_objects(pagination: PaginationDep, app_id: Optional[int] = None):
    # return await RestrictedObjectModel.from_queryset(RestrictedObject.all())
    objects = await restricted_object.query_get_multi(**pagination, object_app_id=app_id)
    return await ReadRestrictedObject.from_queryset(objects)


@router.get('/get/objects', response_model=list[ReadRestrictedObject])
async def get_group_allowed_objects(group: AccessGroup = Depends(get_group_by_id)):
    return await access_group.get_allowed_objects(group=group)


@router.put('/edit/objects', response_model=list[ReadRestrictedObject])
async def set_group_allowed_objects(objects_ids: list[int], group: AccessGroup = Depends(get_group_by_id)):
    return await access_group.set_allowed_objects(group=group, objects_ids=objects_ids)


# @router.put(
#     '/edit/groups',
#     dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:users'])]
# )
# async def set_user_groups(groups_ids: list[int], user: User = Depends(get_user_by_id)):
#     await crud_user.set_user_groups(user, groups_ids)
#     return await user.groups


