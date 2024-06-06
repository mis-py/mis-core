from loguru import logger

from core.db.dataclass import AppState
from core.dependencies.services import get_module_service
from libs.modules.module_service import Modulery


async def init_modules_root_model():
    # TODO CRITICAL need call this method to init models!
    """
    Method called by system loader!
    Creates DB model instance and bind it to module instance and module components
    """
    module_uow_service = get_module_service()
    for module_name, loaded_module in Modulery._loaded_modules.items():
        module_model, is_created = await module_uow_service.get_or_create(name=module_name)
        if is_created:
            module_model.state = AppState.PRE_INITIALIZED
        logger.debug(f"[ModuleService] Module: {module_name} DB instance received")
        await loaded_module.instance.bind_model(module_model, is_created)
        # Modulery._loaded_modules[module_name].model = module_model
        # logger.debug(f"[ModuleService] Module: {module_name} DB instance binded")