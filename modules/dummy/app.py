from loguru import logger

from const import DEFAULT_ADMIN_USERNAME
from core.services.base.unit_of_work import unit_of_work_factory
from core.services.guardian_service import GAccessGroupService, GuardianService
from core.services.user import UserService
from libs.modules.GenericModule import GenericModule
from libs.modules.components import Variables, ModuleLogs, TortoiseModels, EventRoutingKeys, APIRoutes

from .config import UserSettings, RoutingKeys, ModuleSettings
from .routes import router
from .consumers import event_consumers
from .db.models import DummyModel
from .service import DummyService
from .tasks import scheduled_tasks

app_settings = ModuleSettings()
user_settings = UserSettings()
routing_keys = RoutingKeys()


async def init(module_instance: GenericModule):
    pass
    # TODO move it to endpoints
    # uow = unit_of_work_factory()
    #
    # guardian_uow_service = GAccessGroupService(uow)
    # user_uow_service = UserService(uow)
    # admin = await user_uow_service.get(username=DEFAULT_ADMIN_USERNAME)
    #
    # # create access group for module objects
    # # TODO this is constantly creating new group at startup
    # group = await guardian_uow_service.create_with_users(
    #     name="Dummy group",
    #     users_ids=[admin.id],
    # )
    #
    # # create example object
    # dummy_object_1 = await DummyService().create_by_kwargs(dummy_string="Dummy 1")
    #
    # # allow access to object for group
    # await GuardianService(uow).assign_perm('read', group, dummy_object_1)
    # await GuardianService(uow).assign_perm('edit', group, dummy_object_1)
    #
    # # check group access on object
    # is_read_perm = await GuardianService(uow).has_perm('read', group, dummy_object_1)
    # is_edit_perm = await GuardianService(uow).has_perm('edit', group, dummy_object_1)
    # is_delete_perm = await GuardianService(uow).has_perm('delete', group, dummy_object_1)
    # logger.info(f"{group.name} read={is_read_perm} edit={is_edit_perm} delete={is_delete_perm}")

module = GenericModule(
    pre_init_components=[
        TortoiseModels(),
    ],
    components=[
        scheduled_tasks,
        event_consumers,
        APIRoutes(router),
        # just create plain component, all work will be in init() method
        # we declare that module has models in module.db package
        Variables(app_settings, user_settings),
        ModuleLogs(),
        EventRoutingKeys(routing_keys),
    ],
    init_event=init
)
