from typing import Annotated, Optional
from fastapi.params import Depends, Query

from core.dependencies.services import get_user_service, get_team_service, get_module_service, \
    get_g_access_group_service
from core.dependencies.routing_key_service import get_routing_key_service
from core.exceptions import NotFound, ValidationFailed, MISError
from core.services.guardian_service import GAccessGroupService
from core.services.module import ModuleService
from core.services.user import UserService
from core.services.team import TeamService
from core.services.notification import RoutingKeyService


async def get_user_by_id(user_service: Annotated[UserService, Depends(get_user_service)], user_id: int):
    user = await user_service.get(id=user_id)
    if not user:
        raise NotFound('User not found')
    return user


async def get_team_by_id(team_service: Annotated[TeamService, Depends(get_team_service)], team_id: int):
    team = await team_service.get(id=team_id, prefetch_related=['users'])
    if not team:
        raise NotFound('Team not found')
    return team


async def get_module_by_id(
        module_service: Annotated[ModuleService, Depends(get_module_service)],
        module_id: Optional[int] = None,
        module_name: Optional[str] = None,
):
    if module_id:
        module = await module_service.get(id=module_id)
    elif module_name:
        module = await module_service.get(name=module_name)
    else:
        raise ValidationFailed("module_id or module_name is required")

    if not module:
        raise NotFound('Module not found')
    elif module.name == 'core':
        raise MISError("Operations on 'core' module not allowed from 'module_service'")
    return module


async def get_routing_key_by_id(
        routing_key_service: Annotated[ModuleService, Depends(get_routing_key_service)],
        key_id: int
):
    rk = await routing_key_service.get(id=key_id)
    if not rk:
        raise NotFound('RoutingKey not found')
    return rk


async def get_group_by_id(
        g_access_group_service: Annotated[GAccessGroupService, Depends(get_g_access_group_service)],
        group_id: int = Query(),
):
    group = await g_access_group_service.get(id=group_id)
    if not group:
        raise NotFound('Group not found')
    return group


async def pagination_parameters(skip: int = 0, limit: int = 100) -> dict:
    return {"skip": skip, "limit": limit}


PaginationDep = Annotated[dict, Depends(pagination_parameters)]
