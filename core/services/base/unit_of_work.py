from abc import ABC, abstractmethod

from tortoise.transactions import in_transaction

from core.repositories.user import IUserRepository, UserRepository
from core.repositories.team import ITeamRepository, TeamRepository
from core.repositories.variable import IVariableRepository, VariableRepository
from core.repositories.variable_value import IVariableValueRepository, VariableValueRepository
from core.repositories.permission import IPermissionRepository, PermissionRepository
from core.repositories.granted_permission import IGrantedPermissionRepository, GrantedPermissionRepository
from core.repositories.routing_key import IRoutingKeyRepository, RoutingKeyRepository
from core.repositories.routing_key_subscription import IRoutingKeySubscriptionRepository, \
    RoutingKeySubscriptionRepository
from core.repositories.scheduled_job import IScheduledJobRepository, ScheduledJobRepository
from core.repositories.module import IModuleRepository, ModuleRepository
from core.repositories.guardian_permission import IGPermissionRepository, GPermissionRepository
from core.repositories.guardian_content_type import IGContentTypeRepository, GContentTypeRepository
from core.repositories.guardian_access_group import IGAccessGroupRepository, GAccessGroupRepository
from core.repositories.guardian_user_permission import IGUserPermissionRepository, GUserPermissionRepository
from core.repositories.guardian_group_permission import IGGroupPermissionRepository, GGroupPermissionRepository

from core.db.models import (
    User,
    Team,
    Variable,
    VariableValue,
    RoutingKey,
    RoutingKeySubscription,
    ScheduledJob,
    Module
)
from core.db.guardian import (
    GuardianPermission,
    GuardianContentType,
    GuardianAccessGroup,
    GuardianUserPermission,
    GuardianGroupPermission,
)
from core.db.permission import Permission, GrantedPermission


class IUnitOfWork(ABC):
    user_repo: IUserRepository
    team_repo: ITeamRepository
    variable_repo: IVariableRepository
    variable_value_repo: IVariableValueRepository
    permission_repo: IPermissionRepository
    granted_permission_repo: IGrantedPermissionRepository
    routing_key_repo: IRoutingKeyRepository
    routing_key_subscription_repo: IRoutingKeySubscriptionRepository
    scheduled_job_repo: IScheduledJobRepository
    module_repo: IModuleRepository
    g_permission_repo: IGPermissionRepository
    g_content_type_repo: IGContentTypeRepository
    g_access_group_repo: IGAccessGroupRepository
    g_user_permission_repo: IGUserPermissionRepository
    g_group_permission_repo: IGGroupPermissionRepository

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError


class TortoiseUnitOfWork(IUnitOfWork):
    def __init__(self):
        self._in_transaction = in_transaction()
        self.user_repo = UserRepository(model=User)
        self.team_repo = TeamRepository(model=Team)
        self.variable_repo = VariableRepository(model=Variable)
        self.variable_value_repo = VariableValueRepository(model=VariableValue)
        self.permission_repo = PermissionRepository(model=Permission)
        self.granted_permission_repo = GrantedPermissionRepository(model=GrantedPermission)
        self.routing_key_repo = RoutingKeyRepository(model=RoutingKey)
        self.routing_key_subscription_repo = RoutingKeySubscriptionRepository(model=RoutingKeySubscription)
        self.scheduled_job_repo = ScheduledJobRepository(model=ScheduledJob)
        self.module_repo = ModuleRepository(model=Module)
        self.g_permission_repo = GPermissionRepository(model=GuardianPermission)
        self.g_content_type_repo = GContentTypeRepository(model=GuardianContentType)
        self.g_access_group_repo = GAccessGroupRepository(model=GuardianAccessGroup)
        self.g_user_permission_repo = GUserPermissionRepository(model=GuardianUserPermission)
        self.g_group_permission_repo = GGroupPermissionRepository(model=GuardianGroupPermission)

    async def __aenter__(self):
        await self._in_transaction.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._in_transaction.__aexit__(exc_type, exc_val, exc_tb)

    async def commit(self):
        await self._in_transaction.connection.commit()

    async def rollback(self):
        await self._in_transaction.connection.rollback()


def unit_of_work_factory() -> IUnitOfWork:
    return TortoiseUnitOfWork()
