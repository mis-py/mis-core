from typing import Annotated

from fastapi import Depends, APIRouter, Security, Query

from core.db.models import Team, User, Module
from core.dependencies.security import get_current_user
from core.dependencies.path import get_team_by_id, get_user_by_id
from core.dependencies.services import get_variable_service, get_variable_value_service, get_team_service, \
    get_user_service, get_module_service
from core.dependencies.path import get_module_by_id
from core.schemas.variable import VariableResponse, VariableValueResponse
from core.schemas.variable import UpdateVariable
from core.services.module import ModuleService
from core.services.team import TeamService
from core.services.user import UserService

from core.services.variable import VariableService
from core.services.variable_value import VariableValueService
from core.utils.schema import MisResponse, PageResponse
from core.exceptions.exceptions import ValidationFailed, MISError

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
    '/',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:variables'])],
    response_model=PageResponse[VariableResponse]
)
async def get_global_variables(
        variable_service: Annotated[VariableService, Depends(get_variable_service)],
        module_service: Annotated[ModuleService, Depends(get_module_service)],
        # is_global: bool = Query(default=None),
        module_id: int = Query(default=None),
        module_name: str = Query(default=None),
):
    if module_id is not None:
        module_instance = await module_service.get_or_raise(id=module_id)
    elif module_name is not None:
        module_instance = await module_service.get_or_raise(name=module_name)
    else:
        module_instance = None

    return await variable_service.filter_and_paginate(
        # is_global=is_global,
        app_id=module_instance.pk if module_instance else None,
    )


@router.get(
    '/values',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:variables'])],
    response_model=PageResponse[VariableValueResponse],
    description="Returns all available variables by specified filter criteria"
)
async def get_local_variables(
        variable_value_service: Annotated[VariableValueService, Depends(get_variable_value_service)],
        team_service: Annotated[TeamService, Depends(get_team_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        team_id: int = Query(default=None),
        user_id: int = Query(default=None),
):
    if sum(1 for x in [team_id, user_id] if x) != 1:
        raise MISError("Use only one filter")

    if team_id is not None:
        await team_service.get_or_raise(id=team_id)

    if user_id is not None:
        await user_service.get_or_raise(id=user_id)

    return await variable_value_service.filter_and_paginate(
        team_id=team_id,
        user_id=user_id,
        prefetch_related=['variable']
    )


@router.put(
    '/',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:variables'])],
    response_model=MisResponse
)
async def set_global_variables(
        variable_service: Annotated[VariableService, Depends(get_variable_service)],
        module_service: Annotated[ModuleService, Depends(get_module_service)],
        variables: list[UpdateVariable],
        module_id: int = Query(default=None)
):
    if module_id is not None:
        if module_id == 1:
            raise ValidationFailed(f"Module ID '1' has no editable variables")

        module = await module_service.get_or_raise(id=module_id)

        await variable_service.set_variables(module=module, variables=variables)

    return MisResponse()


@router.put(
    '/values',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:variables'])],
    response_model=MisResponse
)
async def set_local_variables(
        variable_value_service: Annotated[VariableValueService, Depends(get_variable_value_service)],
        team_service: Annotated[TeamService, Depends(get_team_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        variables: list[UpdateVariable],
        team_id: int = Query(default=None),
        user_id: int = Query(default=None),
):
    if sum(1 for x in [team_id, user_id] if x) != 1:
        raise MISError("Use only one filter")

    if team_id is not None:
        team = await team_service.get_or_raise(id=team_id, prefetch_related=['users'])

        await variable_value_service.set_variables_values(team=team, variables=variables)

    if user_id is not None:
        user = await user_service.get_or_raise(id=user_id)

        await variable_value_service.set_variables_values(user=user, variables=variables)

    return MisResponse()


@router.get(
    '/my',
    response_model=PageResponse[VariableResponse]
)
async def get_my_variables(
        variable_value_service: Annotated[VariableValueService, Depends(get_variable_value_service)],
        user: User = Depends(get_current_user)
):
    return await variable_value_service.filter_and_paginate(
        user_id=user.pk,
        prefetch_related=['variable']
    )


@router.put(
    '/my',
    response_model=MisResponse
)
async def edit_my_variables(
        variable_value_service: Annotated[VariableValueService, Depends(get_variable_value_service)],
        variables: list[UpdateVariable],
        user: User = Depends(get_current_user)
):
    await variable_value_service.set_variables_values(user=user, variables=variables)

    return MisResponse()
