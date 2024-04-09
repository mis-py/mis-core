import loguru
from tortoise.expressions import Q

from .utils import type_convert

from core.db.models import User, Module, Team, VariableValue, Variable


class VariableSet:
    def __init__(self, user: User = None, app: Module = None, team: Team = None):
        self._user: User = user
        self._app: Module = app
        self._team: Team = team

    async def load(self):
        # getting default_value of setting
        query = Variable.all()

        # if app specified filter to contain only that app settings
        if self._app:
            query = query.filter(app=self._app)

        # set attributes from Setting default_values
        for setting in await query:
            converted_value = type_convert(to_type=setting.type, value=setting.default_value)
            setattr(self, setting.key, converted_value)

        # now apply defined settings
        query = VariableValue.all()

        if self._user:
            if self._user.team_id:
                query = query.filter(Q(user=self._user) | Q(team_id=self._user.team_id))
            else:
                query = query.filter(user=self._user)

        if self._team:
            query = query.filter(team=self._team)

        if self._app:
            query = query.filter(setting__app=self._app)

        settings = await query.order_by('team_id').select_related('setting')

        # set attributes from SettingValue values
        for setting in settings:
            converted_value = type_convert(to_type=setting.setting.type, value=setting.value)
            setattr(self, setting.setting.key, converted_value)

    async def set(self, key, value):
        setting_value, is_created = await VariableValue.get_or_create(
            defaults={'value': value},
            setting=await Variable.get(key=key),
            user=self._user
        )

        if not is_created:
            setting_value.value = value
            await setting_value.save()

        return setting_value
