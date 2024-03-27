from abc import ABC, abstractmethod

from tortoise.transactions import in_transaction

from core.db.models import User, Team, Variable, VariableValue, RoutingKey, RoutingKeySubscription, ScheduledJob, Module
from core.db.permission import Permission, GrantedPermission
from core.repositories.user import IUserRepository, UserRepository
from core.repositories.team import ITeamRepository, TeamRepository
from core.repositories.variable import IVariableRepository, VariableRepository
from core.repositories.variable_value import IVariableValueRepository, VariableValueRepository
from core.repositories.permission import IPermissionRepository, PermissionRepository
from core.repositories.granted_permission import IGrantedPermissionRepository, GrantedPermissionRepository
from core.repositories.routing_key import IRoutingKeyRepository, RoutingKeyRepository
from core.repositories.routing_key_subscription import IRoutingKeySubscriptionRepository, \
    RoutingKeySubscriptionRepository
from core.repositories.schedule_job import IScheduleJobRepository, ScheduleJobRepository
from core.repositories.module import IModuleRepository, ModuleRepository


class IUnitOfWork(ABC):
    user_repo: IUserRepository
    team_repo: ITeamRepository
    variable_repo: IVariableRepository
    variable_value_repo: IVariableValueRepository
    permission_repo: IPermissionRepository
    granted_permission_repo: IGrantedPermissionRepository
    routing_key_repo: IRoutingKeyRepository
    routing_key_subscription_repo: IRoutingKeySubscriptionRepository
    schedule_job_repo: IScheduleJobRepository
    module_repo: IModuleRepository

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
        self.schedule_job_repo = ScheduleJobRepository(model=ScheduledJob)
        self.module_repo = ModuleRepository(model=Module)

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
