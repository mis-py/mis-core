from fastapi import Depends, APIRouter, Security


from core.crud import variables, variable_value
from core.db.models import Team, User, Module
from core.dependencies import get_team_by_id, get_user_by_id, get_current_user
from core.dependencies.path import get_app_by_id, PaginationDep
from core.exceptions import NotFound, ValidationFailed
from core.schemas.variable import UpdateVariableModel, VariableValueModel, VariableModel

from services.modules.module_service import ModuleService
from services.variables.variables import VariablesManager
from services.variables.utils import type_convert

router = APIRouter()


@router.get(
    '',
    dependencies=[Security(get_current_user)],
    response_model=list[VariableModel]
)
async def get_all_variables(pagination: PaginationDep):
    query = await variables.query_get_multi(**pagination)
    return await VariableModel.from_queryset(query)


@router.get(
    '/my',
    response_model=list[VariableValueModel]
)
async def get_my_variables(pagination: PaginationDep, user: User = Depends(get_current_user)):
    query = await variable_value.query_get_multi(**pagination, user=user)
    return await VariableValueModel.from_queryset(query)


@router.put(
    '/my',
    response_model=list[UpdateVariableModel]
)
async def edit_my_variables(data: list[UpdateVariableModel], user: User = Depends(get_current_user)):
    variable_value.set_variables_values(data, user)
    await VariablesManager.update_variables(user=user)


@router.get(
    '/app',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=list[VariableModel]
)
async def get_app_variables(pagination: PaginationDep, app: Module = Depends(get_app_by_id)):
    query = await variables.query_get_multi(**pagination, app=app)
    return await VariableModel.from_queryset(query)


@router.put(
    '/app',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=list[UpdateVariableModel]
)
async def set_default_value(variable_data: list[UpdateVariableModel], app: Module = Depends(get_app_by_id)):
    module = ModuleService.loaded_apps()[app.name]
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
    response_model=list[VariableValueModel],
    dependencies=[Security(get_current_user, scopes=['core:sudo'])]
)
async def get_user_variables(pagination: PaginationDep, user: User = Depends(get_user_by_id)):
    query = await variable_value.query_get_multi(**pagination, user=user)
    return await VariableValueModel.from_queryset(query)


@router.put(
    '/user',
    response_model=list[UpdateVariableModel],
    dependencies=[Security(get_current_user, scopes=['core:sudo'])]
)
async def update_user_variable(
        data: list[UpdateVariableModel],
        user: User = Depends(get_user_by_id),
):
    variable_value.set_variables_values(data, user)
    await VariablesManager.update_variables(user=user)


@router.get(
    '/team',
    response_model=list[VariableValueModel],
    dependencies=[Security(get_current_user, scopes=['core:sudo'])]
)
async def get_team_variables(pagination: PaginationDep, team: Team = Depends(get_team_by_id)):
    query = await variable_value.query_get_multi(**pagination, team=team)
    return await VariableValueModel.from_queryset(query)


@router.put(
    '/team',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=list[UpdateVariableModel]
)
async def update_team_variables(
        data: list[UpdateVariableModel],
        team: Team = Depends(get_team_by_id)
):
    variable_value.set_variables_values(data, team)
    await VariablesManager.update_variables(team=team)
