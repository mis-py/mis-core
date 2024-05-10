from loguru import logger

from const import DEFAULT_ADMIN_USERNAME
from core.dependencies.services import get_g_access_group_service, get_user_service, get_guardian_service
from core.services.guardian_service import GAccessGroupService, GuardianService
from core.services.user import UserService
from services.modules.utils import GenericModule
from services.modules.components import Variables, ModuleLogs, TortoiseModels, EventRoutingKeys

from .config import UserSettings, RoutingKeys, ModuleSettings
from .routes import routes
from .consumers import event_consumers
from .db import DummyModel
from .tasks import scheduled_tasks

app_settings = ModuleSettings()
user_settings = UserSettings()
routing_keys = RoutingKeys()


async def init(module_instance: GenericModule):

    g_access_group_service: GAccessGroupService = get_g_access_group_service()
    guardian_service: GuardianService = get_guardian_service()
    user_service: UserService = get_user_service()

    admin = await user_service.get(username=DEFAULT_ADMIN_USERNAME)

    # create access group for module objects
    group = await g_access_group_service.create_with_users(
        name="Dummy group",
        users_ids=[admin.id],
    )

    # create example object
    dummy_object_1, _ = await DummyModel.get_or_create(dummy_string="Dummy 1")

    # allow access to object for group
    await guardian_service.assign_perm('read', group, dummy_object_1)
    await guardian_service.assign_perm('edit', group, dummy_object_1)

    # check group access on object
    is_read_perm = await guardian_service.has_perm('read', group, dummy_object_1)
    is_edit_perm = await guardian_service.has_perm('edit', group, dummy_object_1)
    is_delete_perm = await guardian_service.has_perm('delete', group, dummy_object_1)
    logger.info(f"{group.name} read={is_read_perm} edit={is_edit_perm} delete={is_delete_perm}")

module = GenericModule(
    pre_init_components=[
        TortoiseModels(),
    ],
    components=[
        scheduled_tasks,
        event_consumers,
        routes,
        # just create plain component, all work will be in init() method
        # we declare that module has models in module.db package
        Variables(app_settings, user_settings),
        ModuleLogs(),
        EventRoutingKeys(routing_keys),
    ],
    init_event=init
)
