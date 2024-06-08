from loguru import logger

from const import MODULES_DIR

from libs.tortoise_manager import TortoiseManager
from ..Base.BaseComponent import BaseComponent


class TortoiseModels(BaseComponent):

    async def pre_init(self, application):
        logger.debug(f"[{self.module.name}] Pre-Initialising models")

        await TortoiseManager.add_models(self.module.name, [f'modules.{self.module.name}.db.models'])
        await TortoiseManager.add_migrations(self.module.name, str(MODULES_DIR / self.module.name / "migrations"))

    async def init(self, app_db_model, is_created: bool):
        pass

    async def start(self):
        pass

    async def stop(self):
        pass

    async def shutdown(self):
        pass
