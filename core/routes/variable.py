from fastapi import Depends, APIRouter, Security, Query

from core.db.models import Team, User, Module
from core.dependencies import get_team_by_id, get_user_by_id, get_current_user
from core.dependencies.misc import UnitOfWorkDep
from core.dependencies.path import get_module_by_id
from core.schemas.variable import VariableResponse, VariableValueResponse
from core.schemas.variable import UpdateVariable

from core.services.variable import VariableService
from core.services.variable_value import VariableValueService
from core.utils.schema import MisResponse, PageResponse
from core.exceptions.exceptions import ValidationFailed, MISError
from services.variables.variables import VariablesManager


router = APIRouter()

# Main idea of variables:
# Every module except Core can provide local and global variables.
# Global variables acts as default value, used by all local variables.
# Local variables acts as copy of global variable, that is binded to user or team.
# Using priority: Local user variable > Local team variable > Global variable
# Also if variable not set it will take value from upper recursivley.

# With endpoints admins can:
# view and edit global variables
# view and edit team local variables
# view and edit user local variables


@router.get(
    '/global',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=PageResponse[VariableResponse]
)
async def get_global_variables(
        uow: UnitOfWorkDep,
        is_global: bool = Query(default=None),
        module_id: int = Query(default=None),
):
    if module_id is not None:
        await get_module_by_id(module_id)

    return await VariableService(uow).filter_and_paginate(
        is_global=is_global,
        app_id=module_id
    )


@router.get(
    '/local',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=PageResponse[VariableValueResponse],
    description="Returns all available variables by specified filter criteria"
)
async def get_local_variables(
        uow: UnitOfWorkDep,
        team_id: int = Query(default=None),
        user_id: int = Query(default=None),
):
    if sum(1 for x in [team_id, user_id] if x) != 1:
        raise MISError("Use only one filter")

    if team_id is not None:
        await get_team_by_id(team_id)

    if user_id is not None:
        await get_user_by_id(user_id)

    return await VariableValueService(uow).filter_and_paginate(
        team_id=team_id,
        user_id=user_id,
        prefetch_related=['setting']
    )


@router.put(
    '/global',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=MisResponse
)
async def set_global_variables(
        uow: UnitOfWorkDep,
        variables: list[UpdateVariable],
        module_id: int = Query(default=None)
):
    if module_id is not None:
        if module_id == 1:
            raise ValidationFailed(f"Module ID '1' has no editable variables")

        module = await get_module_by_id(module_id)

        await VariableService(uow).set_variables(variables=variables)
        await VariablesManager.update_variables(app=module)

    return MisResponse()


@router.put(
    '/local',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=MisResponse
)
async def set_local_variables(
        uow: UnitOfWorkDep,
        variables: list[UpdateVariable],
        team_id: int = Query(default=None),
        user_id: int = Query(default=None),
):
    if sum(1 for x in [team_id, user_id] if x) != 1:
        raise MISError("Use only one filter")

    if team_id is not None:
        team = await get_team_by_id(team_id)

        await VariableValueService(uow).set_variables_values(team_id=team.pk, variables=variables)
        await VariablesManager.update_variables(team=team)

    if user_id is not None:
        user = await get_user_by_id(user_id)

        await VariableValueService(uow).set_variables_values(user_id=user.pk, variables=variables)
        await VariablesManager.update_variables(user=user)

    return MisResponse()


@router.get(
    '/my',
    response_model=PageResponse[VariableResponse]
)
async def get_my_variables(
        uow: UnitOfWorkDep,
        user: User = Depends(get_current_user)
):
    return await VariableValueService(uow).filter_and_paginate(
        user_id=user.pk,
        prefetch_related=['setting']
    )


@router.put(
    '/my',
    response_model=MisResponse
)
async def edit_my_variables(
        uow: UnitOfWorkDep,
        variables: list[UpdateVariable],
        user: User = Depends(get_current_user)
):
    await VariableValueService(uow).set_variables_values(user_id=user.pk, variables=variables)
    await VariablesManager.update_variables(user=user)

    return MisResponse()
