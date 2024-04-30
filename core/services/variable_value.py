from core.db.models import Variable
from core.exceptions import ValidationFailed, NotFound
from core.schemas.variable import UpdateVariable
from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork
from services.variables.utils import type_convert


class VariableValueService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.variable_value_repo)
        self.uow = uow

    async def set_variables_values(
            self,
            variables: list[UpdateVariable],
            user_id: int = None,
            team_id: int = None,
    ):
        """Set variables for user or team"""

        for variable in variables:
            # remove VariableValue if new_value is empty
            if not variable.new_value:
                await self.uow.variable_value_repo.delete(user_id=user_id, setting_id=variable.setting_id)
                continue

            variable_obj = await self.uow.variable_repo.get(id=variable.setting_id)

            await self.validate_variable(variable=variable, variable_obj=variable_obj)

            await self.uow.variable_value_repo.update_or_create(
                variable_id=variable_obj.pk,
                value=variable.new_value,
                user_id=user_id,
                team_id=team_id,
            )

    async def validate_variable(self, variable: UpdateVariable, variable_obj: Variable):
        if not variable_obj:
            raise NotFound(f"VariableValue with ID '{variable.setting_id}' not exist")

        try:
            type_convert(value=variable.new_value, to_type=variable_obj.type)
        except ValueError:
            raise ValidationFailed(
                f"Can't convert value '{variable.new_value}' to '{variable_obj.type}' for VariableValue with ID '{variable.setting_id}'",
            )

        if variable_obj.is_global:
            raise ValidationFailed(
                f"Can't set global VariableValue with ID '{variable.setting_id}' as local setting for user",
            )

