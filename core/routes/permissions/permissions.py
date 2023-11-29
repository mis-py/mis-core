from fastapi import APIRouter, Depends, Security


from core.db import User, Team, crud
from core.db.crud import crud_permission
from core.db.schemas import GrantedPermissionModel, PermissionModel
from core.dependencies import get_user_by_id, get_team_by_id, get_current_user
from core.dependencies.path import PaginationDep
from core.routes.permissions.schema import UpdatePermissionModel

router = APIRouter()


@router.get('', dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])])
async def permissions_list(pagination: PaginationDep):
    return await PermissionModel.from_queryset(await crud_permission.query_get_multi(**pagination))


@router.get('/my', response_model=list[GrantedPermissionModel])
async def get_my_permissions(user: User = Depends(get_current_user)):
    return await GrantedPermissionModel.from_queryset(await user.granted_permissions())


@router.get('/get/user', response_model=list[GrantedPermissionModel],
            dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])])
async def get_user_permissions(user: User = Depends(get_user_by_id)):
    return await GrantedPermissionModel.from_queryset(await user.granted_permissions())


@router.put('/edit/user', response_model=list[GrantedPermissionModel],
            dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])])
async def set_user_permissions(
        data: list[UpdatePermissionModel],
        user: User = Depends(get_user_by_id)
):
    for permission in data:
        if user.id == 1 and permission.permission_id == 1:
            continue

        perm = await crud_permission.get(id=permission.permission_id)

        if permission.granted:
            await user.add_permission(perm.scope)
        else:
            await user.remove_permission(perm.scope)
    return await GrantedPermissionModel.from_queryset(await user.granted_permissions())


@router.get('/get/team', response_model=list[GrantedPermissionModel],
            dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])])
async def get_team_permissions(team: Team = Depends(get_team_by_id)):
    return await GrantedPermissionModel.from_queryset(await team.granted_permissions())


@router.put('/edit/team', response_model=list[GrantedPermissionModel],
            dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])])
async def set_team_permissions(
        data: list[UpdatePermissionModel],
        team: Team = Depends(get_team_by_id)
):
    for permission in data:

        perm = await crud_permission.get(id=permission.permission_id)

        if permission.granted:
            await team.add_permission(perm.scope)
        else:
            await team.remove_permission(perm.scope)

    return await GrantedPermissionModel.from_queryset(await team.granted_permissions())
