from core.repositories.granted_permission import GrantedPermissionRepository
from core.repositories.guardian_access_group import GAccessGroupRepository
from core.repositories.guardian_content_type import GContentTypeRepository
from core.repositories.guardian_group_permission import GGroupPermissionRepository
from core.repositories.guardian_permission import GPermissionRepository
from core.repositories.guardian_user_permission import GUserPermissionRepository
from core.repositories.module import ModuleRepository
from core.repositories.permission import PermissionRepository
from core.repositories.routing_key import RoutingKeyRepository
from core.repositories.routing_key_subscription import RoutingKeySubscriptionRepository
from core.repositories.scheduled_job import ScheduledJobRepository
from core.repositories.team import TeamRepository
from core.repositories.user import UserRepository
from core.repositories.variable import VariableRepository
from core.repositories.variable_value import VariableValueRepository
from core.services.auth import AuthService
from core.services.granted_permission import GrantedPermissionService
from core.services.guardian_service import GContentTypeService, GPermissionService, GAccessGroupService, \
    GUserPermissionService, GGroupPermissionService, GuardianService
from core.services.module import ModuleService
from core.services.notification import RoutingKeyService, RoutingKeySubscriptionService
from core.services.permission import PermissionService
from core.services.scheduled_job import ScheduledJobService
from core.services.team import TeamService
from core.services.user import UserService
from core.services.variable import VariableService
from core.services.variable_value import VariableValueService


def get_user_service() -> UserService:
    user_repo = UserRepository()

    user_service = UserService(user_repo=user_repo)
    return user_service


def get_team_service() -> TeamService:
    team_repo = TeamRepository()
    user_repo = UserRepository()
    variable_repo = VariableRepository()
    variable_value_repo = VariableValueRepository()

    team_service = TeamService(
        team_repo=team_repo,
        user_repo=user_repo,
        variable_repo=variable_repo,
        variable_value_repo=variable_value_repo,
    )
    return team_service


def get_auth_service() -> AuthService:
    user_repo = UserRepository()

    auth_service = AuthService(user_repo=user_repo)
    return auth_service


def get_variable_service() -> VariableService:
    variable_repo = VariableRepository()

    variable_service = VariableService(variable_repo=variable_repo)
    return variable_service


def get_variable_value_service() -> VariableValueService:
    variable_value_repo = VariableValueRepository()
    variable_repo = VariableRepository()

    variable_value_service = VariableValueService(
        variable_value_repo=variable_value_repo,
        variable_repo=variable_repo,
    )
    return variable_value_service


def get_module_service() -> ModuleService:
    module_repo = ModuleRepository()

    module_service = ModuleService(module_repo=module_repo)
    return module_service


def get_scheduled_job_service() -> ScheduledJobService:
    scheduled_job_repo = ScheduledJobRepository()
    module_repo = ModuleRepository()

    scheduled_job_service = ScheduledJobService(
        scheduled_job_repo=scheduled_job_repo,
        module_repo=module_repo,
    )
    return scheduled_job_service


def get_permission_service() -> PermissionService:
    permission_repo = PermissionRepository()

    permission_service = PermissionService(permission_repo=permission_repo)
    return permission_service


def get_granted_permission_service() -> GrantedPermissionService:
    granted_permission_repo = GrantedPermissionRepository()
    permission_repo = PermissionRepository()

    granted_permission_service = GrantedPermissionService(
        granted_permission_repo=granted_permission_repo,
        permission_repo=permission_repo,
    )
    return granted_permission_service


def get_routing_key_service() -> RoutingKeyService:
    routing_key_repo = RoutingKeyRepository()

    routing_key_service = RoutingKeyService(routing_key_repo=routing_key_repo)
    return routing_key_service


def get_routing_key_subscription_service() -> RoutingKeySubscriptionService:
    routing_key_subscription_repo = RoutingKeySubscriptionRepository()

    routing_key_subscription_service = RoutingKeySubscriptionService(
        routing_key_subscription_repo=routing_key_subscription_repo)
    return routing_key_subscription_service


def get_g_content_type_service() -> GContentTypeService:
    g_content_type_repo = GContentTypeRepository()

    g_content_type_service = GContentTypeService(g_content_type_repo=g_content_type_repo)
    return g_content_type_service


def get_g_permission_service() -> GPermissionService:
    g_permission_repo = GPermissionRepository()

    g_permission_service = GPermissionService(g_permission_repo=g_permission_repo)
    return g_permission_service


def get_g_access_group_service() -> GAccessGroupService:
    g_access_group_repo = GAccessGroupRepository()
    user_repo = UserRepository()

    g_access_group_service = GAccessGroupService(
        g_access_group_repo=g_access_group_repo,
        user_repo=user_repo,
    )
    return g_access_group_service


def get_g_user_permission_service() -> GUserPermissionService:
    g_user_permission_repo = GUserPermissionRepository()
    g_content_type_repo = GContentTypeRepository()
    g_permission_repo = GPermissionRepository()
    user_repo = UserRepository()

    g_user_permission_service = GUserPermissionService(
        g_user_permission_repo=g_user_permission_repo,
        g_content_type_repo=g_content_type_repo,
        g_permission_repo=g_permission_repo,
        user_repo=user_repo,
    )
    return g_user_permission_service


def get_g_group_permission_service() -> GGroupPermissionService:
    g_group_permission_repo = GGroupPermissionRepository()
    g_content_type_repo = GContentTypeRepository()
    g_permission_repo = GPermissionRepository()
    g_access_group_repo = GAccessGroupRepository()
    user_repo = UserRepository()

    g_group_permission_service = GGroupPermissionService(
        g_group_permission_repo=g_group_permission_repo,
        g_content_type_repo=g_content_type_repo,
        g_permission_repo=g_permission_repo,
        g_access_group_repo=g_access_group_repo,
        user_repo=user_repo,
    )
    return g_group_permission_service


def get_guardian_service() -> GuardianService:
    g_user_permission_repo = GUserPermissionRepository()
    g_group_permission_repo = GGroupPermissionRepository()
    g_content_type_repo = GContentTypeRepository()
    g_permission_repo = GPermissionRepository()
    g_access_group_repo = GAccessGroupRepository()

    guardian_service = GuardianService(
        g_user_permission_repo=g_user_permission_repo,
        g_group_permission_repo=g_group_permission_repo,
        g_content_type_repo=g_content_type_repo,
        g_permission_repo=g_permission_repo,
        g_access_group_repo=g_access_group_repo,
    )
    return guardian_service
