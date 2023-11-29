from core.db import Setting, SettingValue, User, Team, App
from core.db.crud.base import CRUDBase


class CRUDSetting(CRUDBase):
    async def get_or_create(
            self, app: App, key: str, default_value: str | int | float, is_global: bool, type: str) -> tuple[Setting, bool]:
        return await self.model.get_or_create(
            app=app,
            key=key,
            default_value=default_value,
            is_global=is_global,
            type=type,
        )

    async def update_params(self, setting: Setting, default_value, is_global: bool, type: str):
        """Update params if old params not equal old params"""
        if (setting.default_value != default_value
                or setting.is_global != is_global
                or setting.type != type):
            setting.default_value = default_value
            setting.is_global = is_global
            setting.type = type
            await setting.save()
        return setting

    async def remove_unused(self, app: App, exist_keys: list[str]):
        """Remove unused setting for app"""
        return await self.model.filter(app=app).exclude(key__in=exist_keys).delete()


crud_setting = CRUDSetting(Setting)


class CRUDSettingValue(CRUDBase):
    async def update_or_create(self, setting: Setting, value, user: User = None, team: Team = None):
        setting_value, is_created = await SettingValue.update_or_create(
            defaults={'value': value},
            setting=setting,
            user=user,
            team=team
        )
        if not is_created:
            setting_value.value = value
            await setting_value.save()
        return setting_value


setting_value = CRUDSettingValue(SettingValue)
