from enum import Enum

from core.db.models import User, Permission, Team, Module
from const import DEFAULT_ADMIN_USERNAME
from core.utils.security import get_password_hash
from config import CoreSettings

settings = CoreSettings()


async def setup_core():
    core = await Module.get_or_none(name='core')
    if core is None:
        core = await Module.create(name='core')
        await Permission.create(name='Superuser permissions', scope='sudo', app=core)
        await Permission.create(name="Access for 'users' endpoints", scope="users", app=core)
        await Permission.create(name="Access for 'teams' endpoints", scope="teams", app=core)
        await Permission.create(name="Access for 'modules' endpoints", scope="modules", app=core)
        await Permission.create(name="Access for 'groups' endpoints", scope="groups", app=core)
        await Permission.create(name="Access for 'notifications' endpoints", scope="notifications", app=core)
        await Permission.create(name="Access for 'logs' endpoints", scope="logs", app=core)
        await Permission.create(name="Access for 'tasks' endpoints", scope="tasks", app=core)
        await Permission.create(name="Access for 'consumers' endpoints", scope="consumers", app=core)
        await Permission.create(name="Access for 'modules' endpoints", scope="modules", app=core)
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


class SettingType(str, Enum):
    str = "str"
    int = "int"
    float = "float"
    bool = "bool"
