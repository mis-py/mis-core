from services.modules.utils import GenericModule
from services.modules.components import Variables, ModuleLogs, TortoiseModels, EventRoutingKeys

from .config import UserSettings, RoutingKeys, ModuleSettings
from .routes import routes
# from .consumers import event_consumers
# from .tasks import scheduled_tasks

app_settings = ModuleSettings()
user_settings = UserSettings()
routing_keys = RoutingKeys()


module = GenericModule(
    pre_init_components=[
        TortoiseModels(),
    ],
    components=[
        # scheduled_tasks,
        # event_consumers,
        routes,
        Variables(app_settings, user_settings),
        ModuleLogs(),
        EventRoutingKeys(routing_keys),
    ]
)