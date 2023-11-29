from fastapi import Depends, APIRouter, Security, Request


from core.db.crud import crud_setting, setting_value
from core.db.models import Team, User, Setting, App
from core.db.schemas import SettingValueModel, SettingModel
from core.dependencies import get_team_by_id, get_user_by_id, get_current_user
from core.dependencies.path import get_app_by_id, PaginationDep
from core.dependencies.security import check_user_perm
from core.exceptions import NotFound, ValidationFailed
from core.routes.variables.schema import UpdateSettingModel

from services.modules.module_service import ModuleService
from services.variables.variables import SettingsManager
from services.variables.utils import type_convert

router = APIRouter()


@router.get('', dependencies=[Security(get_current_user)], response_model=list[SettingModel])
async def get_all_settings(pagination: PaginationDep):
    settings = await crud_setting.query_get_multi(**pagination)
    return await SettingModel.from_queryset(settings)


@router.get('/my', response_model=list[SettingValueModel])
async def get_my_settings(pagination: PaginationDep, user: User = Depends(get_current_user)):
    query = await setting_value.query_get_multi(**pagination, user=user)
    return await SettingValueModel.from_queryset(query)


@router.get('/app', dependencies=[Security(get_current_user, scopes=['core:sudo'])])
async def get_app_settings(pagination: PaginationDep, app: App = Depends(get_app_by_id)):
    settings = await crud_setting.query_get_multi(**pagination, app=app)
    return await SettingModel.from_queryset(settings)


@router.put('/app', dependencies=[Security(get_current_user, scopes=['core:sudo'])])
async def set_default_value(setting_data: list[UpdateSettingModel], request: Request,
                            app: App = Depends(get_app_by_id)):
    module = ModuleService.loaded_apps()[app.name]

    for setting in setting_data:
        setting_model = await crud_setting.get(id=setting.setting_id, app=app)
        if not setting_model:
            raise NotFound(f"Setting {setting.setting_id} is not bound to the app!")

        try:
            converted_value = type_convert(value=setting.new_value, to_type=setting_model.type)
        except ValueError:
            raise ValidationFailed(
                f"Can't set setting {setting_model.key}. Value is not '{setting_model.type}' type"
            )

        await crud_setting.update(setting_model, {"default_value": converted_value})

        setattr(
            module.app_settings,
            setting_model.key,
            setting.new_value
        )

    # TODO what is it for? await misapp.init_settings()
    await SettingsManager.update_settings(app=app)
    return True


@router.get('/user', response_model=list[SettingValueModel],
            dependencies=[Security(get_current_user, scopes=['core:sudo'])])
async def get_user_settings(pagination: PaginationDep, user: User = Depends(get_user_by_id)):
    query = await setting_value.query_get_multi(**pagination, user=user)
    return await SettingValueModel.from_queryset(query)


@router.put('/user')
async def update_user_setting(
        data: list[UpdateSettingModel],
        user: User = Depends(get_user_by_id),
        current_user: User = Depends(get_current_user)
):
    if user.id != current_user.id:
        await check_user_perm(current_user, scopes=['core:sudo'])

    for setting in data:

        # remove SettingValue if new_value is empty
        if not setting.new_value:
            await setting_value.remove(user=user, setting=setting.setting_id)
            continue

        setting_model = await crud_setting.get(id=setting.setting_id)
        if not setting_model:
            raise NotFound(f"Setting {setting.setting_id} is not bound to the user!")

        await set_setting_value(
            setting_model,
            setting.new_value, user=user
        )
    await SettingsManager.update_settings(user=user)


@router.get('/team', response_model=list[SettingValueModel],
            dependencies=[Security(get_current_user, scopes=['core:sudo'])])
async def get_team_settings(pagination: PaginationDep, team: Team = Depends(get_team_by_id)):
    query = await setting_value.query_get_multi(**pagination, team=team)
    return await SettingValueModel.from_queryset(query)


@router.put('/team', dependencies=[Security(get_current_user, scopes=['core:sudo'])])
async def update_team_setting(
        data: list[UpdateSettingModel],
        team: Team = Depends(get_team_by_id)
):
    for setting in data:
        # remove SettingValue if new_value is empty
        if not setting.new_value:
            await setting_value.remove(team=team, setting=setting.setting_id)
            continue

        setting_model = await crud_setting.get(id=setting.setting_id)
        if not setting_model:
            raise NotFound(f"Setting {setting.setting_id} is not bound to the team!")

        await set_setting_value(
            setting_model,
            setting.new_value, team=team
        )
    await SettingsManager.update_settings(team=team)


async def set_setting_value(setting: Setting, value, user: User = None, team: Team = None):
    try:
        converted_value = type_convert(value=value, to_type=setting.type)
    except ValueError:
        raise ValidationFailed(
            f"Can't set setting {setting.key}. Value is not '{setting.type}' type",
        )

    if setting.is_global:
        raise ValidationFailed(
            f"Can't set global setting {setting.key} as local setting for user",
        )

    await setting_value.update_or_create(
        setting=setting,
        value=converted_value,
        user=user,
        team=team,
    )
