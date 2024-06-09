from fastapi import Depends

from core.db.models import Module, User
from core.dependencies.misc import get_current_app
from core.dependencies.security import get_current_user
from core.dependencies.variable_service import get_variable_service
from core.dependencies.routing_key_service import get_routing_key_service
from core.utils.app_context import AppContext
from libs.eventory import Eventory


async def get_userless_app_context(
        module: Module = Depends(get_current_app),
):
    variable_service = get_variable_service()
    routing_key_service = get_routing_key_service()
    return AppContext(
        app_name=module.name,
        variables=await variable_service.make_variable_set(app=module),
        routing_keys=await routing_key_service.make_routing_keys_set(module=module),
        user=None,
        team=None
    )


async def get_app_context(
        user: User = Depends(get_current_user),
        module: Module = Depends(get_current_app),
):
    """Context for jobs and other services.
    If user or team is defined then variables will be available in context along with module variables"""
    variable_service = get_variable_service()
    routing_key_service = get_routing_key_service()
    await user.fetch_related('team')

    return AppContext(
        app_name=module.name,
        user=user,
        team=user.team,
        variables=await variable_service.make_variable_set(user=user, team=user.team, app=module),
        routing_keys=await routing_key_service.make_routing_keys_set(module=module)
    )
