from pydoc import locate

from loguru import logger
from pydantic import Field, create_model, TypeAdapter
from tortoise.expressions import Subquery, Q

from core.db.models import User, Module, Team, Variable, VariableValue
from core.repositories.variable import IVariableRepository
from core.repositories.variable_value import IVariableValueRepository
from core.schemas.variable import UpdateVariable
from core.services.base.base_service import BaseService
from core.services.variable_callback_manager import VariableCallbackManager
from core.utils.common import exclude_none_values
from core.exceptions import NotFound, ValidationFailed
from core.utils.variable_set import VariableSet


class VariableService(BaseService):
    """Need for update all VariableSet objects when variables changed"""
    _variables: list[VariableSet] = []

    def __init__(self, variable_repo: IVariableRepository, variable_value_repo: IVariableValueRepository):
        self.variable_repo = variable_repo
        self.variable_value_repo = variable_value_repo
        super().__init__(repo=variable_repo)

    async def set_variables(
            self,
            module: Module,
            variables: list[UpdateVariable]
    ):
        """Set global variables for module"""

        for variable_in in variables:
            variable_obj = await self.get(id=variable_in.variable_id)

            await self.validate_variable(variable_in, variable_obj)

            await self.variable_value_repo.update_or_create(
                variable_id=variable_obj.pk,
                value=variable_in.new_value,
                user_id=None,
                team_id=None,
            )

            await self.update_variable_sets(variable_obj.key, variable_in.new_value, app=module)

            await VariableCallbackManager.trigger(
                module_name=module.name,
                variable_key=variable_obj.key,
                new_value=variable_in.new_value,
            )

    async def set_variables_values(
            self,
            variables: list[UpdateVariable],
            user: User = None,
            team: Team = None,
    ):
        """Set local variables for user or team"""

        for variable_value in variables:
            # remove VariableValue if new_value is empty
            if not variable_value.new_value:
                # TODO shoud team_id passed here to remove empty variable value?
                await self.variable_value_repo.delete(user_id=user.id, variable_id=variable_value.variable_id)
                continue

            variable = await self.variable_repo.get(id=variable_value.variable_id, prefetch_related=['app'])

            await self.validate_local_variable(variable=variable_value, variable_obj=variable)

            await self.variable_value_repo.update_or_create(
                variable_id=variable.pk,
                value=variable_value.new_value,
                user_id=user.id if user else None,
                team_id=team.id if team else None,
            )

            await self.update_variable_sets(variable.key, variable_value.new_value, user, team)

            await VariableCallbackManager.trigger(
                module_name=variable.app.name,
                variable_key=variable.key,
                new_value=variable_value.new_value,
            )

    async def validate_variable(self, variable: UpdateVariable, variable_obj: Variable):
        if not variable_obj:
            raise NotFound(f"VariableValue with ID '{variable.variable_id}' not exist")

        # validate value
        variable_type = locate(variable_obj.type)
        variable_value = variable.new_value
        TypeAdapter(type=variable_type).validate_python(variable_value)

    async def validate_local_variable(self, variable: UpdateVariable, variable_obj: Variable):
        await self.validate_variable(variable=variable, variable_obj=variable_obj)
        if variable_obj.is_global:
            raise ValidationFailed(
                f"Can't set global VariableValue with ID '{variable.variable_id}' as local setting for user",
            )

    async def get_or_create_variable(
            self,
            module_id: int,
            key: str,
            default_value: str | int | float,
            is_global: bool,
            variable_type: str
    ):
        return await self.variable_repo.get_or_create(
            module_id=module_id,
            key=key,
            default_value=default_value,
            is_global=is_global,
            type=variable_type,
        )

    async def update_variable(self, variable: Variable, default_value, is_global: bool, type: str):
        """Update params if new params not equal old params"""
        if variable.default_value != default_value or variable.is_global != is_global or variable.type != type:
            await self.variable_repo.update(
                id=variable.pk,
                data={
                    'default_value': default_value,
                    'is_global': is_global,
                    'type': type,
                },
            )
        return variable

    async def filter_variable(self, prefetch_related: list[str] = None, **filters) -> list[Variable]:
        filters_without_none = exclude_none_values(filters)
        return await self.variable_repo.filter(prefetch_related=prefetch_related, **filters_without_none)

    async def filter_variable_value(self, prefetch_related: list[str] = None, **filters) -> list[VariableValue]:
        filters_without_none = exclude_none_values(filters)
        return await self.variable_value_repo.filter(prefetch_related=prefetch_related, **filters_without_none)

    async def delete_unused_variables(self, module_id: int, exist_keys: list[str]) -> int:
        """Remove unused variables for app"""
        return await self.variable_repo.delete_unused(module_id=module_id, exist_keys=exist_keys)

    async def update_variable_sets(self, variable_key, new_value, user=None, team=None, app=None):
        for variable_set in self._variables:
            if not variable_set.is_bind(user, team, app):
                continue

            dict_model = variable_set.model_dump()
            dict_model.update({variable_key: new_value})

            variable_set.model_validate(dict_model)

            logger.debug(f"updating value of '{variable_key}' from '{getattr(variable_set, variable_key, None)}' to '{new_value}'")
            setattr(variable_set, variable_key, new_value)

    async def make_variable_set(self, app: Module, user: User = None, team: Team = None) -> VariableSet:
        # Get variables from app
        subfilter = await self.variable_repo.filter_queryable(app=app)
        variables = await subfilter

        # Get any values if exists
        query = await self.variable_value_repo.filter_queryable(variable_id__in=Subquery(subfilter.values('id')))

        if user:
            if user.team_id:
                query = query.filter(Q(user=user) | Q(team_id=user.team_id))
            else:
                query = query.filter(user=user)

        if team:
            query = query.filter(team=team)

        variable_values: list[VariableValue] = await query.select_related('variable')

        # Extend by global variable values
        global_variables_query = await self.variable_value_repo.filter_queryable(user=None, team=None)
        global_variable_values: list[VariableValue] = await global_variables_query.select_related('variable')
        variable_values.extend(global_variable_values)

        # Construct pydantic fields structure
        fields = {
            variable.key: (
                locate(variable.type),
                Field(
                    default=variable.default_value,
                    title=variable.key,
                )
            ) for variable in variables
        }

        # Construct value data
        values = {
            variable_value.variable.key: variable_value.value for variable_value in variable_values
        }

        # Construct pydentic model
        VariableValuesSet = create_model(
            'VariableValuesSet',
            __base__=VariableSet,
            **fields
        )

        # Initialize model with data
        variable_set = VariableValuesSet(
            app=app,
            user=user,
            team=team,
            **values
        )

        self._variables.append(variable_set)

        return variable_set
