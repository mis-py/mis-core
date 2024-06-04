from core.db.models import User, Module, Team, Variable
from core.exceptions import ValidationFailed, NotFound
from core.repositories.variable import IVariableRepository
from core.repositories.variable_value import IVariableValueRepository
from core.schemas.variable import UpdateVariable
from core.services.base.base_service import BaseService
from core.utils.types import type_convert
from core.utils.variable_set import VariableSet


class VariableValueService(BaseService):
    """Need for update all VariableSet objects when variables changed"""
    _variables: list[VariableSet] = []

    def __init__(self, variable_value_repo: IVariableValueRepository, variable_repo: IVariableRepository):
        self.variable_value_repo = variable_value_repo
        self.variable_repo = variable_repo
        super().__init__(repo=variable_value_repo)

    async def set_variables_values(
            self,
            variables: list[UpdateVariable],
            user: User = None,
            team: Team = None,
    ):
        """Set variables for user or team"""

        for variable in variables:
            # remove VariableValue if new_value is empty
            if not variable.new_value:
                # TODO shoud team_id passed here to remove empty variable value?
                await self.variable_value_repo.delete(user_id=user.id, variable_id=variable.variable_id)
                continue

            variable_obj = await self.variable_repo.get(id=variable.variable_id)


            await self.validate_variable(variable=variable, variable_obj=variable_obj)

            await self.variable_value_repo.update_or_create(
                variable_id=variable_obj.pk,
                value=variable.new_value,
                user_id=user.id,
                team_id=team.id,
            )

        await self.update_variable_sets(user, team)

    async def validate_variable(self, variable: UpdateVariable, variable_obj: Variable):
        if not variable_obj:
            raise NotFound(f"VariableValue with ID '{variable.variable_id}' not exist")

        try:
            type_convert(value=variable.new_value, to_type=variable_obj.type)
        except ValueError:
            raise ValidationFailed(
                f"Can't convert value '{variable.new_value}' to '{variable_obj.type}' for VariableValue with ID '{variable.variable_id}'",
            )

        if variable_obj.is_global:
            raise ValidationFailed(
                f"Can't set global VariableValue with ID '{variable.variable_id}' as local setting for user",
            )

    async def update_variable_sets(self, user=None, team=None, app=None):
        for variable in self._variables:
            if user and user != variable._user:
                continue
            elif team and (team != variable._team and variable._user not in team.users):
                continue
            elif app and app != variable._app:
                continue
            await variable.load()

    async def make_variable_set(self, user: User = None, app: Module = None, team: Team = None) -> VariableSet:
        variable_set = VariableSet(user=user, team=team, app=app)
        await variable_set.load()
        self._variables.append(variable_set)
        return variable_set
