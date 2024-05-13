from abc import ABC

from core.db.models import VariableValue
from core.repositories.base.repository import IRepository, TortoiseORMRepository


class IVariableValueRepository(IRepository, ABC):
    async def update_or_create(self, variable_id: int, value, user_id: int = None, team_id: int = None):
        raise NotImplementedError()


class VariableValueRepository(TortoiseORMRepository, IVariableValueRepository):
    model = VariableValue

    async def update_or_create(self, variable_id: int, value, user_id: int = None, team_id: int = None):
        variable_value_instance, is_created = await self.model.update_or_create(
            defaults={'value': value},
            variable_id=variable_id,
            user_id=user_id,
            team_id=team_id
        )
        if not is_created:
            variable_value_instance.value = value
            await variable_value_instance.save()
        return variable_value_instance
