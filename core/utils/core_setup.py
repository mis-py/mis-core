from tortoise import Tortoise

from const import DEFAULT_ADMIN_USERNAME
from core import crud
from config import CoreSettings
from core.db.mixin import GuardianMixin
from core.db.models import Module, User, Team
from core.db.permission import Permission
from core.utils.common import camel_to_spaces
from core.utils.security import get_password_hash


settings = CoreSettings()


async def setup_core():
    core = await Module.get_or_none(name='core')
    if core is None:
        # Create core app as enabled and already running
        core = await Module.create(name='core', enabled=True, state=Module.AppState.RUNNING)
        await Permission.create(name='Superuser permissions', scope='sudo', app=core)
        await Permission.create(name="Access for 'users' endpoints", scope="users", app=core)
        await Permission.create(name="Access for 'teams' endpoints", scope="teams", app=core)
        await Permission.create(name="Access for 'modules' endpoints", scope="modules", app=core)
        await Permission.create(name="Access for 'groups' endpoints", scope="groups", app=core)
        await Permission.create(name="Access for 'notifications' endpoints", scope="notifications", app=core)
        await Permission.create(name="Access for 'logs' endpoints", scope="logs", app=core)
        await Permission.create(name="Access for 'tasks' endpoints", scope="tasks", app=core)
        await Permission.create(name="Access for 'consumers' endpoints", scope="consumers", app=core)
        await Permission.create(name="Access for 'permissions' endpoints", scope="permissions", app=core)

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

            content_type, _ = await crud.guardian_content_type.get_or_create(
                module=module,
                model=model_name,
            )
            model_name_spaces = camel_to_spaces(model_name)

            for code_perm_name in default_perms_map:
                await crud.guardian_permissions.get_or_create(
                    code_name=code_perm_name,
                    name=f"Can {code_perm_name} {model_name_spaces}",
                    content_type=content_type,
                )


async def setup_events():
    pass
    # TODO implement
