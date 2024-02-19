from loguru import logger
import os
from core.db.models import User, Module, Team, Variable

from .variable_set import VariableSet


class VariablesManager:
    """Need for update all VariableSet objects when variables changed"""
    _variables: list[VariableSet] = []

    @classmethod
    async def init(cls):
        async for variable in Variable.filter(default_value__isnull=False):
            logger.debug(f' - variable {variable.key} -> {variable.default_value}')
            os.environ.setdefault(variable.key, variable.default_value)

    @classmethod
    def add_variable_set(cls, variable_set: VariableSet):
        cls._variables.append(variable_set)

    @classmethod
    async def update_variables(cls, user=None, team=None, app=None):
        for variable in cls._variables:
            if user and user != variable._user:
                continue
            elif team and (team != variable._team and variable._user not in team.users):
                continue
            elif app and app != variable._app:
                continue
            await variable.load()

    @classmethod
    async def make_variable_set(cls, user: User = None, app: Module = None, team: Team = None) -> VariableSet:
        variable_set = VariableSet(user=user, team=team, app=app)
        await variable_set.load()
        cls.add_variable_set(variable_set)
        return variable_set
