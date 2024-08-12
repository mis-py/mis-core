from core.services.variable_callbacks import change_module_logs
from core.utils.module import GenericModule
from core.utils.module.components import Variables, ModuleLogs, TortoiseModels, EventRoutingKeys

from .config import UserSettings, RoutingKeys, ModuleSettings
from .routes import api_router
from .shared.shared_logic import shared_manager

# from .consumers import event_consumers
# from .tasks import scheduled_tasks

app_settings = ModuleSettings()
user_settings = UserSettings()
routing_keys = RoutingKeys()


module = GenericModule(
    pre_init_components=[
        TortoiseModels(),
        api_router,
    ],
    components=[
        api_router,
        # scheduled_tasks,
        # event_consumers,
        Variables(
            app_settings, user_settings,
            observers={'LOG_LEVEL': change_module_logs}
        ),
        ModuleLogs(),
        EventRoutingKeys(routing_keys),
        shared_manager,
    ]
)