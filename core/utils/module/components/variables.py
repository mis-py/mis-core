import itertools
from typing import Callable

from loguru import logger

from const import DEFAULT_ADMIN_USERNAME
from core.dependencies.services import get_permission_service, get_user_service
from core.dependencies.variable_service import get_variable_service
from core.services.permission import PermissionService
from core.services.user import UserService
from core.services.variable import VariableService
from core.services.variable_callback_manager import VariableCallbackManager
from core.utils.common import pydatic_model_to_dict
from ..Base.BaseComponent import BaseComponent


class Variables(BaseComponent):
    def __init__(self, module_variables, user_variables, observers: dict[str, Callable] = None):
        self.module_variables = module_variables
        self.user_variables = user_variables
        self.observers = observers or {}

    async def pre_init(self, application):
        pass

    async def init(self, app_db_model, is_created: bool):
        logger.debug(f'[Variables] Connecting variables for {self.module.name}')

        await self.save_permissions(app_db_model)
        await self.save_variables(app_db_model)

        for variable_key, observer in self.observers.items():
            await VariableCallbackManager.register(
                module_name=app_db_model.name,
                variable_key=variable_key,
                callback=observer,
            )

        logger.debug(f'[Variables] Variables connected for {self.module.name}')

    async def start(self):
        pass

    async def stop(self):
        pass

    async def shutdown(self):
        pass

    async def save_permissions(self, app_model):
        permission_service: PermissionService = get_permission_service()
        user_service: UserService = get_user_service()
        admin_user = await user_service.get(username=DEFAULT_ADMIN_USERNAME)

        exist_permission_ids = []
        for scope, description in self.module.permissions.items():
            perm = await permission_service.update_or_create(
                module=app_model,
                name=description,
                scope=scope,
            )
            logger.debug(f'[Variables] Created permission {scope} for {self.module.name}')

            # add only sudo scopes to admin user
            if scope == 'sudo':
                await admin_user.add_permission(f'{app_model.name}:{scope}')

            exist_permission_ids.append(perm.id)

        logger.debug(f'[Variables] Permissions saved for {self.module.name}')

        deleted_count = await permission_service.delete_unused(
            module_id=app_model.pk, exist_ids=exist_permission_ids)
        logger.debug(f'[Variables] Deleted {deleted_count} unused permissions for {self.module.name}')

    async def save_variables(self, app_model):
        variable_service: VariableService = get_variable_service()

        app_variables, user_variables = dict(self.module_variables), dict(self.user_variables)
        variables = itertools.chain(app_variables.items(), user_variables.items())

        typed_variables = {
            **pydatic_model_to_dict(self.user_variables),
            **pydatic_model_to_dict(self.module_variables),
        }

        for key, default_value in variables:
            variable_type = typed_variables[key]["type"]
            is_global = key in app_variables
            variable, is_created = await variable_service.get_or_create_variable(
                module_id=app_model.pk,
                key=key,
                default_value=default_value,
                is_global=is_global,
                variable_type=variable_type
            )
            if not is_created:
                await variable_service.update_variable(
                    variable=variable,
                    default_value=default_value,
                    is_global=is_global,
                    type=variable_type
                )

            logger.debug(f'[Variables] Variable saved {key} ({default_value}) for {self.module.name}')

        deleted_count = await variable_service.delete_unused_variables(
            module_id=app_model.pk, exist_keys=[*app_variables.keys(), *user_variables.keys()],
        )
        logger.debug(f'[Variables] Deleted {deleted_count} unused variables for {self.module.name}')
