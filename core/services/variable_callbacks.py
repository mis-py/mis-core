from config import CoreSettings
from const import MODULES_DIR
from libs.logs.filters import PathLoguruFilter
from libs.logs.manager import LogManager

core_settings = CoreSettings()


async def change_module_logs(module_name: str, new_value: str):
    module_path_filter = PathLoguruFilter(MODULES_DIR / module_name)
    LogManager.set_loggers(
        name=module_name,
        level=new_value,
        filter=module_path_filter,
        format=core_settings.LOGGER_FORMAT,
        rotation=core_settings.LOG_ROTATION,
    )
