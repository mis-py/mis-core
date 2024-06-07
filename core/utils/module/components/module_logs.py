import re

from loguru import logger
from config import CoreSettings
from const import LOGS_DIR

from core.utils.module import get_app_context
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
        def filter_module_logs(x):
            matched = re.match('modules\\.(.+?(?=\\.))', x['name'])
            if matched:
                return matched.group(1) == self.module.name

        ctx: AppContext = await get_app_context(app=app_db_model)

        logger.add(
            LOGS_DIR / f"{self.module.name}/{self.module.name}.log",
            format=core_settings.LOGGER_FORMAT,
            rotation=core_settings.LOG_ROTATION,
            level=ctx.variables.LOG_LEVEL,
            filter=filter_module_logs,
            serialize=True,
        )

    async def start(self):
        pass

    async def stop(self):
        pass

    async def shutdown(self):
        pass
