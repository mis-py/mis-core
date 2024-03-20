from core.services import guardian_service
from core.services.guardian import assign_perm, has_perm
from services.modules.utils import ModuleTemplate
from services.modules.components import Variables, ModuleLogs, TortoiseModels, EventRoutingKeys

from .config import UserSettings, RoutingKeys, ModuleSettings
from .routes import routes
from .consumers import event_consumers
from .db import DummyModel
from .tasks import scheduled_tasks

app_settings = ModuleSettings()
user_settings = UserSettings()
routing_keys = RoutingKeys()


async def init(module_instance: ModuleTemplate):
    # create access group for module objects
    group = await guardian_service.create_group(
        name="Dummy group",
        users_ids=[0],
        module=module_instance.model
    )

    # create example object
    dummy_object_1, _ = await DummyModel.get_or_create(dummy_string="Dummy 1")

    # allow access to object for group
    await assign_perm('read', group, dummy_object_1)
    await assign_perm('edit', group, dummy_object_1)

    # check group access on object
    is_read_perm = await has_perm('read', group, dummy_object_1)
    is_edit_perm = await has_perm('edit', group, dummy_object_1)
    is_delete_perm = await has_perm('delete', group, dummy_object_1)
    # logger.info(f"{group.name} read={is_read_perm} edit={is_edit_perm} delete={is_delete_perm}")

module = ModuleTemplate(
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
