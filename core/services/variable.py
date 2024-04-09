from core.db.models import Variable
from core.schemas.variable import UpdateVariable
from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork
from services.variables.utils import type_convert
from core.exceptions import NotFound, ValidationFailed


class VariableService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.variable_repo)
        self.uow = uow

    async def set_variables(self, variables: list[UpdateVariable]):
        for variable in variables:

            variable_obj = await self.get(id=variable.setting_id)

            converted_value = await self.validate_variable(variable, variable_obj)

            await self.uow.variable_repo.update(
                id=variable_obj.id,
                data={'default_value': converted_value},
            )

    async def validate_variable(self, variable: UpdateVariable, variable_obj: Variable):
        if not variable_obj:
            raise NotFound(f"Variable with ID '{variable.setting_id}' is not exist")

        try:
            return type_convert(value=variable.new_value, to_type=variable_obj.type)
        except ValueError:
            raise ValidationFailed(
                f"Can't convert value '{variable.new_value}' to '{variable_obj.type}' for Variable with ID '{variable.setting_id}'",
            )
