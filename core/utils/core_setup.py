from typing import Annotated

from tortoise import Tortoise

from const import DEFAULT_ADMIN_USERNAME
from config import CoreSettings
from core.db.guardian import GuardianPermission, GuardianContentType
from core.db.mixin import GuardianMixin
from core.db.models import Module, User, Team
from core.dependencies.services import get_module_service, get_permission_service
from core.services.module import ModuleService
from core.services.permission import PermissionService
from core.utils.common import camel_to_spaces
from core.utils.security import get_password_hash


settings = CoreSettings()


async def setup_core():
    module_service: ModuleService = get_module_service()
    permission_service: PermissionService = get_permission_service()

    core = await module_service.get(name='core')
    if core is None:
        # Create core app as enabled and already running
        core = await module_service.create_core(name='core')

        await permission_service.create_with_scope(name='Superuser permissions', scope='sudo', module=core)
        await permission_service.create_with_scope(name="Access for 'users' endpoints", scope="users", module=core)
        await permission_service.create_with_scope(name="Access for 'teams' endpoints", scope="teams", module=core)
        await permission_service.create_with_scope(name="Access for 'modules' endpoints", scope="modules", module=core)
        await permission_service.create_with_scope(name="Access for 'groups' endpoints", scope="groups", module=core)
        await permission_service.create_with_scope(name="Access for 'notifications' endpoints", scope="notifications", module=core)
        await permission_service.create_with_scope(name="Access for 'logs' endpoints", scope="logs", module=core)
        await permission_service.create_with_scope(name="Access for 'tasks' endpoints", scope="tasks", module=core)
        await permission_service.create_with_scope(name="Access for 'consumers' endpoints", scope="consumers", module=core)
        await permission_service.create_with_scope(name="Access for 'permissions' endpoints", scope="permissions", module=core)

    return core is None


async def setup_admin_user():
    if not await User.get_or_none(username=DEFAULT_ADMIN_USERNAME):
        team = await Team.create(name='Superusers')
        user = await User.create(
            username=DEFAULT_ADMIN_USERNAME,
            team=team,
            hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD)
        )

        await user.set_permissions(['core:sudo'])
        await team.set_permissions(['core:sudo'])


async def setup_guardian():
    """Creating rows in ContentType and Permissions"""

    default_perms_map = ('read', 'edit', 'delete')

    models_using_guardian_mixin = GuardianMixin.get_all_subclasses()

    for app, models in Tortoise.apps.items():
        if app == 'models':
            module_name = 'core'
        else:
            module_name = app
        module = await Module.get(name=module_name)

        for model_name, model in models.items():
            if model not in models_using_guardian_mixin:
                continue

            content_type, _ = await GuardianContentType.get_or_create(
                module=module,
                model=model_name,
            )
            model_name_spaces = camel_to_spaces(model_name)

            for code_perm_name in default_perms_map:
                await GuardianPermission.get_or_create(
                    code_name=code_perm_name,
                    name=f"Can {code_perm_name} {model_name_spaces}",
                    content_type=content_type,
                )


async def setup_events():
    pass
    # TODO implement
