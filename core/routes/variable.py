from fastapi import Depends, APIRouter, Security, Query
from fastapi_pagination import Page

from core.crud import variables, variable_value
from core.db.models import Team, User, Module
from core.dependencies import get_team_by_id, get_user_by_id, get_current_user
from core.dependencies.misc import UnitOfWorkDep
from core.dependencies.path import get_app_by_id, PaginationDep
from core.exceptions import NotFound, ValidationFailed
from core.schemas.variable import UpdateVariableModel, VariableValueModel, VariableModel, VariableResponse
from core.schemas.variable_value import VariableValueResponse
from core.services.variable import VariableService
from core.services.variable_value import VariableValueService

from services.modules.module_service import ModuleService
from services.variables.variables import VariablesManager
from services.variables.utils import type_convert

router = APIRouter()


@router.get(
    '',
    dependencies=[Security(get_current_user)],
    response_model=Page[VariableResponse]
)
async def get_all_variables(
        uow: UnitOfWorkDep,
        is_global: bool = Query(default=None)
):
    return await VariableService(uow).filter_and_paginate(is_global=is_global)


@router.get(
    '/my',
    response_model=Page[VariableValueResponse]
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
)
async def edit_my_variables(
        uow: UnitOfWorkDep,
        variables: list[UpdateVariableModel],
        user: User = Depends(get_current_user)
):
    await VariableValueService(uow).set_variables_values(user_id=user.pk, variables=variables)
    await VariablesManager.update_variables(user=user)
    return True


@router.get(
    '/app',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=Page[VariableModel]
)
async def get_app_variables(uow: UnitOfWorkDep, app: Module = Depends(get_app_by_id)):
    return await VariableService(uow).filter_and_paginate(
        app_id=app.pk,
    )


@router.put(
    '/app',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=list[UpdateVariableModel]
)
async def set_default_value(variable_data: list[UpdateVariableModel], app: Module = Depends(get_app_by_id)):
    module = ModuleService.loaded_modules()[app.name]
    updated_variables = list()
    for variable in variable_data:
        variable_model = await variables.get(id=variable.setting_id, app=app)
        if not variable_model:
            raise NotFound(f"Setting {variable.setting_id} is not bound to the app!")

        try:
            converted_value = type_convert(value=variable.new_value, to_type=variable_model.type)
        except ValueError:
            raise ValidationFailed(
                f"Can't set setting {variable_model.key}. Value is not '{variable_model.type}' type"
            )

        await variables.update(variable_model, {"default_value": converted_value})

        setattr(
            module.app_settings,
            variable_model.key,
            variable.new_value
        )

        updated_variables.append(variable)

    # TODO what is it for? -> await misapp.init_settings()
    await VariablesManager.update_variables(app=app)
    return updated_variables


@router.get(
    '/user',
    response_model=Page[VariableValueResponse],
    dependencies=[Security(get_current_user, scopes=['core:sudo'])]
)
async def get_user_variables(
        uow: UnitOfWorkDep,
        user: User = Depends(get_user_by_id)
):
    return await VariableValueService(uow).filter_and_paginate(
        user_id=user.pk,
        prefetch_related=['setting']
    )


@router.put(
    '/user',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])]
)
async def update_user_variable(
        uow: UnitOfWorkDep,
        variables: list[UpdateVariableModel],
        user: User = Depends(get_user_by_id),
):
    await VariableValueService(uow).set_variables_values(user_id=user.pk, variables=variables)
    await VariablesManager.update_variables(user=user)
    return True


@router.get(
    '/team',
    response_model=Page[VariableValueModel],
    dependencies=[Security(get_current_user, scopes=['core:sudo'])]
)
async def get_team_variables(uow: UnitOfWorkDep, team: Team = Depends(get_team_by_id)):
    return await VariableValueService(uow).filter_and_paginate(
        team_id=team.pk,
        prefetch_related=['setting']
    )


@router.put(
    '/team',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
)
async def update_team_variables(
        uow: UnitOfWorkDep,
        variables: list[UpdateVariableModel],
        team: Team = Depends(get_team_by_id)
):
    await VariableValueService(uow).set_variables_values(team_id=team.pk, variables=variables)
    await VariablesManager.update_variables(team=team)
    return True
