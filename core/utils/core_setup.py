import os

from aiormq import DuplicateConsumerTag
from loguru import logger
from tortoise import Tortoise

from const import DEFAULT_ADMIN_USERNAME, MODULES_DIR, MODULES_DIR_NAME
from config import CoreSettings
from core.consumers import core_event_consumers
from core.db.guardian import GuardianPermission, GuardianContentType
from core.db.mixin import GuardianMixin
from core.db.dataclass import AppState
from core.db.models import Module, User, Team
from core.dependencies.services import get_module_service, get_permission_service
from core.services.module import ModuleService
from core.services.permission import PermissionService
from core.utils.common import camel_to_spaces
from core.utils.security import get_password_hash
from core.utils.module.utils import manifests_sort_by_dependency, import_module, unload_module, read_module_manifest, \
    module_dependency_check, get_app_context
from libs.eventory import Eventory

settings = CoreSettings()


async def setup_core():
    module_service: ModuleService = get_module_service()
    permission_service: PermissionService = get_permission_service()

    core = await module_service.get(name='core')
    if core is None:
        # Create core app as enabled and already running
        core = await module_service.create_core(name='core')

        await permission_service.create_with_scope(name='Superuser permissions', scope='sudo', module=core)
        await permission_service.create_with_scope(name="Access for 'users' endpoints", scope="users", module=core)
        await permission_service.create_with_scope(name="Access for 'teams' endpoints", scope="teams", module=core)
        await permission_service.create_with_scope(name="Access for 'modules' endpoints", scope="modules", module=core)
        await permission_service.create_with_scope(name="Access for 'notifications' endpoints", scope="notifications", module=core)
        await permission_service.create_with_scope(name="Access for 'logs' endpoints", scope="logs", module=core)
        await permission_service.create_with_scope(name="Access for 'tasks' endpoints", scope="tasks", module=core)
        await permission_service.create_with_scope(name="Access for 'consumers' endpoints", scope="consumers", module=core)
        await permission_service.create_with_scope(name="Access for 'permissions' endpoints", scope="permissions", module=core)
        await permission_service.create_with_scope(name="Access for 'guardian' endpoints", scope="guardian", module=core)
        await permission_service.create_with_scope(name="Access for 'jobs' endpoints", scope="jobs", module=core)
        await permission_service.create_with_scope(name="Access for 'variables' endpoints", scope="variables", module=core)

    await setup_core_consumers(core)

    return core is None


async def setup_admin_user():
    if not await User.get_or_none(username=DEFAULT_ADMIN_USERNAME):
        team = await Team.create(name='Superusers')
        user = await User.create(
            username=DEFAULT_ADMIN_USERNAME,
            team=team,
            hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD)
        )

        await user.set_permissions(['core:sudo'])
        await team.set_permissions(['core:sudo'])


async def setup_guardian():
    """Creating rows in ContentType and Permissions"""

    default_perms_map = ('read', 'edit', 'delete')

    models_using_guardian_mixin = GuardianMixin.get_all_subclasses()

    for app, models in Tortoise.apps.items():
        if app == 'models':
            module_name = 'core'
        else:
            module_name = app
        module = await Module.get(name=module_name)

        for model_name, model in models.items():
            if model not in models_using_guardian_mixin:
                continue

            content_type, _ = await GuardianContentType.get_or_create(
                module=module,
                model=model_name,
            )
            model_name_spaces = camel_to_spaces(model_name)

            for code_perm_name in default_perms_map:
                await GuardianPermission.get_or_create(
                    code_name=code_perm_name,
                    name=f"Can {code_perm_name} {model_name_spaces}",
                    content_type=content_type,
                )


async def setup_manifest_init():
    """
    Method called by system loader!
    Collect manifest.json files from each module in modules directory
    """

    manifests = {}
    for module in os.listdir(MODULES_DIR):
        if "__" in module:
            continue
        manifest = read_module_manifest(module)

        if not manifest:
            continue
        manifests[module] = manifest

    # we need to load modules in specific order, so we sort it by dependency tree
    # sort func adds module that not exist
    sorted_module_manifests = manifests_sort_by_dependency(manifests)

    # validation dependency version
    for module_name, manifest in sorted_module_manifests.items():
        is_valid_dependency_version = module_dependency_check(
            module_manifest=manifest, all_manifests=sorted_module_manifests
        )
        if not is_valid_dependency_version:
            continue

        ModuleService.add_manifest(module_name, manifest)


async def setup_modules_pre_init(application):
    """
    Method called by system loader!
    Import modules by sorted manifests and run pre init for each module
    """

    for module_name in ModuleService.get_loaded_module_names():
        package = import_module(module_name, MODULES_DIR_NAME)
        instance = package.module

        ModuleService.add_instance(module_name, instance)

        logger.debug(f'[ModuleService] Module: {module_name} pre_init started!')
        await instance.pre_init(application)
        logger.debug(f"[ModuleService] Module: '{module_name}' pre_init finished!")


async def setup_modules_models():
    """
    Method called by system loader!
    Creates DB model instance and bind it to module instance and module components
    """
    module_service = get_module_service()
    for module_name in ModuleService.get_loaded_module_names():
        instance = ModuleService.get_loaded_module(module_name).instance
        if not instance:
            logger.debug(f"Module: {module_name} instance is None, skip..")
            continue

        module_model, is_created = await module_service.get_or_create(name=module_name)
        if is_created:
            module_model.state = AppState.PRE_INITIALIZED
        logger.debug(f"Module: {module_name} DB instance received")

        await instance.bind_model(module_model, is_created)
        logger.debug(f"Module: {module_name} DB instance binded")


async def setup_modules_init():
    """
    Method called by system loader!
    Run module init and start if module is enabled
    """

    module_service = get_module_service()
    for module_name in ModuleService.get_loaded_module_names():
        module_model = await module_service.get_or_raise(name=module_name)
        if module_model.enabled:
            try:
                await module_service.init_module(module_name)
            except Exception as e:
                logger.error(f'[ModuleService] Module: {module_name} system init failed ({e}), skip...')
                continue

            logger.debug(f'[ModuleService] Module: {module_name} auto-start is enabled starting...')

            try:
                await module_service.start_module(module_name)
            except Exception as e:
                logger.error(f'[ModuleService] Module: {module_name} system init failed ({e}), skip...')
                continue


async def setup_modules_shutdown():
    """
    Method called by system loader!
    Executes when application shutdowns.
    Calls stop_module for every enabled app if enabled and then shutdown
    """
    module_service = get_module_service()
    for module_name in ModuleService.get_loaded_module_names():
        module_model = await module_service.get_or_raise(name=module_name)
        if module_model.enabled:
            await module_service.stop_module(module_name)
        await module_service.shutdown_module(module_name, from_system=True)


async def setup_core_consumers(core: Module):
    """Register and start eventory consumers"""
    for event in core_event_consumers.events:
        logger.debug(f'[EventManager]: Register consumer {event.func.__name__} from {core.name}')

        context = await get_app_context(module=core)

        consumer = await Eventory.register_consumer(
            func=event.func,
            routing_key=event.route_key,
            channel_name=core.name,
            extra_kwargs={'ctx': context},
        )

        logger.debug(f'[EventManager] Starting consumer {consumer.consumer_tag} from {core.name}')
        try:
            await consumer.start()
        except DuplicateConsumerTag as e:
            logger.error(f"Consumer already exists: {e}")

        core_event_consumers.consumers.append(consumer)
