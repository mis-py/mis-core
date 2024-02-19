from core.db.models import Variable, VariableValue, User, Team, Module
from core.crud.base import CRUDBase
from core.exceptions import ValidationFailed, NotFound
from services.variables.utils import type_convert


class CRUDVariable(CRUDBase):
    async def get_or_create(
            self, app: Module, key: str, default_value: str | int | float, is_global: bool, type: str) -> tuple[Variable, bool]:
        return await self.model.get_or_create(
            app=app,
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
            variable.default_value = default_value
            variable.is_global = is_global
            variable.type = type
            await variable.save()
        return variable

    async def remove_unused(self, app: Module, exist_keys: list[str]):
        """Remove unused variables for app"""
        return await self.model.filter(app=app).exclude(key__in=exist_keys).delete()


variables = CRUDVariable(Variable)


class CRUDVariableValue(CRUDBase):
    async def update_or_create(self, variable: Variable, value, user: User = None, team: Team = None):
        variable_value_instance, is_created = await self.model.update_or_create(
            defaults={'value': value},
            setting=variable,
            user=user,
            team=team
        )
        if not is_created:
            variable_value_instance.value = value
            await variable_value_instance.save()
        return variable_value_instance

    async def set_variable_value(self, variable: Variable, value, user: User = None, team: Team = None):
        try:
            converted_value = type_convert(value=value, to_type=variable.type)
        except ValueError:
            raise ValidationFailed(
                f"Can't set setting {variable.key}. Value is not '{variable.type}' type",
            )

        if variable.is_global:
            raise ValidationFailed(
                f"Can't set global setting {variable.key} as local setting for user",
            )

        await self.update_or_create(
            variable=variable,
            value=converted_value,
            user=user,
            team=team,
        )

    async def set_variables_values(self, data, user: User = None, team: Team = None):
        for variable in data:
            # remove VariableValue if new_value is empty
            if not variable.new_value:
                await self.remove(user=user, team=team, setting=variable.setting_id)
                continue

            variable_model = await variables.get(id=variable.setting_id)

            if not variable_model:
                raise NotFound(f"Setting {variable.setting_id} is not bound to the user!")

            await self.set_variable_value(
                variable_model,
                variable.new_value, user=user, team=team
            )
        # TODO rework if above working bad
        # for variable in data:
        #     # remove SettingValue if new_value is empty
        #     if not variable.new_value:
        #         await self.remove(team=team, variable=variable.setting_id)
        #         continue
        #
        #     variable_model = await crud_setting.get(id=variable.setting_id)
        #     if not variable_model:
        #         raise NotFound(f"Setting {variable.setting_id} is not bound to the team!")
        #
        #     await self.set_setting_value(
        #         variable_model,
        #         variable.new_value, team=team
        #     )


variable_value = CRUDVariableValue(VariableValue)
