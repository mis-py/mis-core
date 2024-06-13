import re

from loguru import logger
from config import CoreSettings
from const import MODULES_DIR

from core.utils.module import get_app_context
from libs.logs.filters import PathLoguruFilter
from libs.logs.manager import LogManager
from ...app_context import AppContext
from ..Base.BaseComponent import BaseComponent


core_settings = CoreSettings()


class ModuleLogs(BaseComponent):
    """
    Module creating separate handler for save module logs to file on disk
    """

    def pre_init(self, application):
        pass

    async def init(self, app_db_model, is_created: bool):
        ctx: AppContext = await get_app_context(module=app_db_model)
        module_path_filter = PathLoguruFilter(MODULES_DIR / self.module.name)
        LogManager.set_loggers(
            name=self.module.name,
            level=ctx.variables.LOG_LEVEL,
            filter=module_path_filter,
            format=core_settings.LOGGER_FORMAT,
            rotation=core_settings.LOG_ROTATION,
        )

    async def start(self):
        pass

    async def stop(self):
        pass

    async def shutdown(self):
        pass
