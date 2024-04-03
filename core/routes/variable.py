from fastapi import Depends, APIRouter, Security, Query

from core.db.models import Team, User, Module
from core.dependencies import get_team_by_id, get_user_by_id, get_current_user
from core.dependencies.misc import UnitOfWorkDep
from core.dependencies.path import get_module_by_id
from core.exceptions import NotFound, ValidationFailed
from core.schemas.variable import UpdateVariableModel, VariableValueModel, VariableModel, VariableResponse
from core.schemas.variable_value import VariableValueResponse
from core.services.variable import VariableService
from core.services.variable_value import VariableValueService
from core.utils.schema import MisResponse, PageResponse

from services.modules.module_service import ModuleService
from services.variables.variables import VariablesManager
from services.variables.utils import type_convert

router = APIRouter()


@router.get(
    '',
    dependencies=[Security(get_current_user)],
    response_model=PageResponse[VariableResponse]
)
async def get_all_variables(
        uow: UnitOfWorkDep,
        is_global: bool = Query(default=None),
        module_id: int = Query(default=None),
):
    return await VariableService(uow).filter_and_paginate(is_global=is_global, app_id=module_id)


@router.get(
    '/my',
    response_model=PageResponse[VariableValueResponse]
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
    response_model=MisResponse[VariableValueModel]
)
async def edit_my_variables(
        uow: UnitOfWorkDep,
        variables: list[UpdateVariableModel],
        user: User = Depends(get_current_user)
):
    variable_value_service = VariableValueService(uow)
    await variable_value_service.set_variables_values(user_id=user.pk, variables=variables)
    await VariablesManager.update_variables(user=user)
    variable_with_related = await variable_value_service.get(
        id=user.pk,
        prefetch_related=['setting']
    )

    return MisResponse[VariableValueModel](result=variable_with_related)


@router.get(
    '/app',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=PageResponse[VariableModel]
)
async def get_app_variables(uow: UnitOfWorkDep, module: Module = Depends(get_module_by_id)):
    return await VariableService(uow).filter_and_paginate(
        app_id=module.pk,
    )


@router.put(
    '/app',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=MisResponse[list[UpdateVariableModel]]
)
async def set_default_value(
        uow: UnitOfWorkDep,
        variables: list[UpdateVariableModel],
        module_model: Module = Depends(get_module_by_id),
):
    module = ModuleService.loaded_modules()[module_model.name]
    updated_variables = list()
    for variable in variables:
        variable_model = await VariableService(uow).get(id=variable.setting_id, app_id=module_model.pk)
        if not variable_model:
            raise NotFound(f"Setting {variable.setting_id} is not bound to the app!")

        try:
            converted_value = type_convert(value=variable.new_value, to_type=variable_model.type)
        except ValueError:
            raise ValidationFailed(
                f"Can't set setting {variable_model.key}. Value is not '{variable_model.type}' type"
            )

        await VariableService(uow).update_default_value(
            variable_id=variable_model.id,
            default_value=converted_value,
        )

        setattr(
            module.app_settings,
            variable_model.key,
            variable.new_value
        )

        updated_variables.append(variable)

    # TODO what is it for? -> await misapp.init_settings()
    await VariablesManager.update_variables(app=module)
    return MisResponse(result=updated_variables)


@router.get(
    '/user',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=PageResponse[VariableValueResponse]
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
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=MisResponse[VariableValueResponse]
)
async def update_user_variable(
        uow: UnitOfWorkDep,
        variables: list[UpdateVariableModel],
        user: User = Depends(get_user_by_id),
):
    variable_value_service = VariableValueService(uow)
    await variable_value_service.set_variables_values(user_id=user.pk, variables=variables)
    await VariablesManager.update_variables(user=user)

    variable_with_related = await variable_value_service.get(
        id=user.pk,
        prefetch_related=['setting']
    )

    return MisResponse[VariableValueModel](result=variable_with_related)


@router.get(
    '/team',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=PageResponse[VariableValueModel]
)
async def get_team_variables(uow: UnitOfWorkDep, team: Team = Depends(get_team_by_id)):
    return await VariableValueService(uow).filter_and_paginate(
        team_id=team.pk,
        prefetch_related=['setting']
    )


@router.put(
    '/team',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=MisResponse
)
async def update_team_variables(
        uow: UnitOfWorkDep,
        variables: list[UpdateVariableModel],
        team: Team = Depends(get_team_by_id)
):
    variable_value_service = VariableValueService(uow)
    await variable_value_service.set_variables_values(team_id=team.pk, variables=variables)
    await VariablesManager.update_variables(team=team)

    variable_with_related = await variable_value_service.get(
        id=team.pk,
        prefetch_related=['setting']
    )

    return MisResponse[VariableValueModel](result=variable_with_related)
