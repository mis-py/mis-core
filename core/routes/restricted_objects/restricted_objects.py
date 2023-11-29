from fastapi import Security, Depends, APIRouter

from core.db import App
from core.db.crud import restricted_object
from core.dependencies import get_current_user
from core.dependencies.path import get_app_by_id, PaginationDep

from .schema import RestrictedObjectModel

router = APIRouter(dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:restricted_objects'])])


@router.get('')
async def get_restricted_objects(pagination: PaginationDep):
    # return await RestrictedObjectModel.from_queryset(RestrictedObject.all())
    objects = await restricted_object.query_get_multi(**pagination)
    return await RestrictedObjectModel.from_queryset(objects)


@router.get('/app_objects')
async def get_app_restricted_objects(pagination: PaginationDep, app: App = Depends(get_app_by_id)):
    # return await RestrictedObjectModel.from_queryset(RestrictedObject.filter(object_app=app))
    objects = await restricted_object.query_get_multi(**pagination, object_app=app)
    return await RestrictedObjectModel.from_queryset(objects)

# @router.get('/group_objects')
# async def get_group_allowed_objects(group: UserGroup = Depends(get_group_by_id)):
#     return await group.allowed_objects
#
#
# @router.put('/group_objects')
# async def set_group_allowed_objects(objects_ids: list[int], group: UserGroup = Depends(get_group_by_id)):
#     await group.allowed_objects.clear()
#
#     objects = await RestrictedObject.filter(id__in=objects_ids)
#     for obj in objects:
#         await obj.allowed_groups.add(group)
#     return await group.allowed_objects
