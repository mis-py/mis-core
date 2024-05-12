from tortoise.expressions import Q

from .utils import type_convert

from core.db.models import User, Module, Team, VariableValue, Variable


class VariableSet:
    def __init__(self, user: User = None, app: Module = None, team: Team = None):
        self._user: User = user
        self._app: Module = app
        self._team: Team = team

    async def load(self):
        # getting default_value of variable
        query = Variable.all()

        # if app specified filter to contain only that app variables
        if self._app:
            query = query.filter(app=self._app)

        # set attributes from variable default_values
        for variable in await query:
            converted_value = type_convert(to_type=variable.type, value=variable.default_value)
            setattr(self, variable.key, converted_value)

        # now apply defined variables
        query = VariableValue.all()

        if self._user:
            if self._user.team_id:
                query = query.filter(Q(user=self._user) | Q(team_id=self._user.team_id))
            else:
                query = query.filter(user=self._user)

        if self._team:
            query = query.filter(team=self._team)

        if self._app:
            query = query.filter(variable__app=self._app)

        variable_values = await query.order_by('team_id').select_related('variable')

        # set attributes from variable values
        for variable_value in variable_values:
            converted_value = type_convert(to_type=variable_value.variable.type, value=variable_value.value)
            setattr(self, variable_value.variable.key, converted_value)

    async def set(self, key, value):
        variable_value, is_created = await VariableValue.get_or_create(
            defaults={'value': value},
            variable=await Variable.get(key=key),
            user=self._user
        )

        if not is_created:
            variable_value.value = value
            await variable_value.save()

        return variable_value
