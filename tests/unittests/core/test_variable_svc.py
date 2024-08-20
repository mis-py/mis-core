from unittest.mock import Mock

import pytest
from tortoise.contrib.test import TestCase

from core.db.models import Module, Variable, VariableValue, Team, User
from core.dependencies.variable_service import get_variable_service
from core.exceptions import ValidationFailed


class TestVariableService(TestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.variable_service = get_variable_service()
        self.module = await Module.create(name='test_module')

    async def test_set_variables(self):
        variable = await Variable.create(key="TEST", app=self.module, type='str')

        variables = [
            Mock(
                variable_id=variable.pk,
                new_value='test_value'
            )
        ]
        await self.variable_service.set_variables(module=self.module, variables=variables)

        variable_value = await VariableValue.filter(variable__app_id=self.module.pk).first()
        assert variable_value.variable_id == variable.pk
        assert variable_value.value == 'test_value'

    async def test_set_variables_values(self):
        variable = await Variable.create(key="TEST", app=self.module, type='str', is_global=False)

        variables = [
            Mock(
                variable_id=variable.pk,
                new_value='test_value'
            )
        ]
        team = await Team.create(name="Team")
        await team.fetch_related('users')

        await self.variable_service.set_variables_values(team=team, variables=variables)

        variable_value = await VariableValue.filter(team_id=team.pk).first()
        assert variable_value.variable_id == variable.pk
        assert variable_value.value == 'test_value'

    async def test_validate_variable_fail(self):
        variable = await Variable.create(key="TEST", app=self.module, type='str', is_global=False)

        variable_data_for_validate = Mock(
            variable_id=variable.pk,
            new_value=1
        )

        with pytest.raises(ValidationFailed):
            await self.variable_service.validate_variable(
                variable=variable_data_for_validate,
                variable_obj=variable,
            )

    async def test_validate_variable_success(self):
        variable = await Variable.create(key="TEST", app=self.module, type='str', is_global=False)

        variable_data_for_validate = Mock(
            variable_id=variable.pk,
            new_value='string_value'
        )

        await self.variable_service.validate_variable(
            variable=variable_data_for_validate,
            variable_obj=variable,
        )

    async def test_get_or_create_variable(self):
        variable, is_created = await self.variable_service.get_or_create_variable(
            module_id=self.module.pk,
            key='TEST',
            default_value='Test',
            is_global=False,
            variable_type='str',
        )
        assert is_created is True
        assert variable.key == 'TEST'
        assert variable.default_value == 'Test'
        assert variable.is_global is False
        assert variable.type == 'str'

    async def test_update_variable(self):
        variable = await Variable.create(key="TEST", app=self.module, type='str', is_global=False)

        updated_variable = await self.variable_service.update_variable(
            variable=variable,
            default_value='test',
            is_global=False,
            type='str',
        )

        assert updated_variable.default_value == 'test'

    async def test_delete_unused_variables(self):
        used_variable = await Variable.create(key='TEST', app=self.module, type='str', is_global=False)
        unused_variable = await Variable.create(key='Unused', app=self.module, type='str', is_global=False)

        await self.variable_service.delete_unused_variables(
            module_id=self.module.pk,
            exist_keys=[used_variable.key],
        )

        is_variable_exists = await self.variable_service.exists(id=unused_variable.pk)
        assert is_variable_exists is False

    async def test_make_variable_set(self):
        await Variable.create(
            key="TEST",
            app=self.module,
            type='str',
            is_global=False,
            default_value='test',
        )
        team = await Team.create(name='Test')
        user = await User.create(username='Test', team_id=team.pk, hashed_password='...')

        variable_set = await self.variable_service.make_variable_set(
            app=self.module,
            user=user,
        )

        assert variable_set.TEST == 'test'

    async def update_variable_sets(self):
        await Variable.create(
            key="TEST",
            app=self.module,
            type='str',
            is_global=False,
            default_value='test',
        )
        team = await Team.create(name='Test')
        user = await User.create(username='Test', team_id=team.pk, hashed_password='...')

        await self.variable_service.make_variable_set(
            app=self.module,
            user=user,
        )

        await self.variable_service.update_variable_sets(
            variable_key='TEST',
            new_value='UpdatedTest',
            user=user,
        )

        assert await self.variable_service._variables[0].TEST == 'UpdatedTest'
