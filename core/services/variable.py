from core.db.models import Variable
from core.repositories.variable import IVariableRepository
from core.schemas.variable import UpdateVariable
from core.services.base.base_service import BaseService
from services.variables.utils import type_convert
from core.exceptions import NotFound, ValidationFailed


class VariableService(BaseService):
    def __init__(self, variable_repo: IVariableRepository):
        self.variable_repo = variable_repo
        super().__init__(repo=variable_repo)

    async def set_variables(self, variables: list[UpdateVariable]):
        for variable in variables:

            variable_obj = await self.get(id=variable.setting_id)

            converted_value = await self.validate_variable(variable, variable_obj)

            await self.variable_repo.update(
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

    async def get_or_create(
            self,
            module_id: int,
            key: str,
            default_value: str | int | float,
            is_global: bool,
            type: str
    ):
        return await self.variable_repo.get_or_create(
            module_id=module_id,
            key=key,
            default_value=default_value,
            is_global=is_global,
            type=type,
        )
    async def update_params(self, variable: Variable, default_value, is_global: bool, type: str):
        """Update params if old params not equal old params"""
        if (variable.default_value != default_value
                or variable.is_global != is_global
                or variable.type != type):
            await self.variable_repo.update(
                id=variable.pk,
                data={
                    'default_value': default_value,
                    'is_global': is_global,
                    'type': type,
                },
            )
        return variable

    async def delete_unused(self, module_id: int, exist_keys: list[str]) -> int:
        """Remove unused variables for app"""
        return await self.variable_repo.delete_unused(module_id=module_id, exist_keys=exist_keys)

