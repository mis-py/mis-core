from loguru import logger

from const import DEFAULT_ADMIN_USERNAME
from core.dependencies.services import get_g_access_group_service, get_guardian_service, get_user_service
from core.services.variable_callbacks import change_module_logs
from core.utils.module import GenericModule
from core.utils.module.components import Variables, ModuleLogs, TortoiseModels, EventRoutingKeys

from .config import UserSettings, RoutingKeys, ModuleSettings
from .consumers import event_consumers
from .dependencies.services import get_dummy_restricted_model_service
from .routes import api_router
from .tasks import scheduled_tasks

app_settings = ModuleSettings()
user_settings = UserSettings()
routing_keys = RoutingKeys()


async def init(module_instance: GenericModule):
    g_access_group_service = get_g_access_group_service()
    guardian_service = get_guardian_service()
    user_service = get_user_service()

    admin = await user_service.get(username=DEFAULT_ADMIN_USERNAME)

    # create access group for module objects
    example_group_name = "Dummy group"
    group = await g_access_group_service.get(name=example_group_name)
    if not group:
        group = await g_access_group_service.create_with_users(
            name=example_group_name, users_ids=[admin.id]
        )

    # create example object
    example_dummy_int = 123
    dummy_restricted_service = get_dummy_restricted_model_service()
    dummy_object_1 = await dummy_restricted_service.get(dummy_int=example_dummy_int)
    if not dummy_object_1:
        dummy_object_1 = await dummy_restricted_service.create_by_kwargs(dummy_int=example_dummy_int)

    # allow access to object for group
    await guardian_service.assign_perm('read', group, dummy_object_1)
    await guardian_service.assign_perm('edit', group, dummy_object_1)

    # check group access on object
    is_read_perm = await guardian_service.has_perm('read', group, dummy_object_1)
    is_edit_perm = await guardian_service.has_perm('edit', group, dummy_object_1)
    is_delete_perm = await guardian_service.has_perm('delete', group, dummy_object_1)
    logger.debug(f"{group.name} read={is_read_perm} edit={is_edit_perm} delete={is_delete_perm}")


module = GenericModule(
    pre_init_components=[
        TortoiseModels(),
        api_router,
    ],
    components=[
        scheduled_tasks,
        event_consumers,
        api_router,
        # just create plain component, all work will be in init() method
        # we declare that module has models in module.db package
        Variables(
            app_settings, user_settings,
            observers={'LOG_LEVEL': change_module_logs}
        ),
        ModuleLogs(),
        EventRoutingKeys(routing_keys),
    ],
    init_event=init
)
