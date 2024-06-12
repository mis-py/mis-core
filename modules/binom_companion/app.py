from core.utils.module.generic_module import GenericModule
from core.utils.module.components import Variables, ModuleLogs, TortoiseModels, EventRoutingKeys

from .config import UserSettings, RoutingKeys, ModuleSettings
from .routes import api_router
from .tasks import scheduled_tasks
from .consumers import event_consumers


app_settings = ModuleSettings()
user_settings = UserSettings()
routing_keys = RoutingKeys()


async def init(module_instance: GenericModule):
    pass


# //  "dependencies": [
# //    {"module": "proxy_registry", "version": "<=0.1,>=0.1"}
# //  ],

module = GenericModule(
    pre_init_components=[
        TortoiseModels(),
        api_router,
    ],
    components=[
        api_router,
        scheduled_tasks,
        event_consumers,
        Variables(app_settings, user_settings),
        ModuleLogs(),
        EventRoutingKeys(routing_keys),
    ],
    init_event=init
)
