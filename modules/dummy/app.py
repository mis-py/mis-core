from core.db.crud import access_group

from services.modules.utils import ModuleTemplate
from services.modules.components import Settings, ModuleLogs, TortoiseModels, EventRoutingKeys

from .config import UserSettings, RoutingKeys, ModuleSettings
from .routes import routes
from .consumers import event_consumers
from .db import DummyRestrictedModel
from .tasks import scheduled_tasks


app_settings = ModuleSettings()
user_settings = UserSettings()
routing_keys = RoutingKeys()


async def init(module_instance: ModuleTemplate):
    # create access group for module objects
    group = await access_group.create_with_users(
        name="Dummy group",
        users_ids=[0],
        app_model=module_instance.model
    )

    # create example object
    dummy_object_1 = await DummyRestrictedModel.get_safe(dummy_restricted_string="Dummy restricted 1")

    # allow access to object for group
    await dummy_object_1.allow(group)

module = ModuleTemplate(
    name="dummy",
    display_name="Dummy",
    description="Module with examples of core functions and libs extensions",
    version="1.0",
    author="Jake Jameson",
    category='example',
    dependencies=[],
    permissions={
        "dummy": "Just for demonstration",
    },
    pre_init_components=[
        TortoiseModels(),
    ],
    components=[
        scheduled_tasks,
        event_consumers,
        routes,
        # just create plain component, all work will be in init() method
        # we declare that module has models in module.db package
        Settings(app_settings, user_settings),
        ModuleLogs(),
        EventRoutingKeys(routing_keys),
    ],
    init_event=init
)
