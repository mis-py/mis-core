from core.db.models import Module
from core.dependencies.variable_service import get_variable_service
from core.utils.app_context import AppContext
from libs.eventory import Eventory


async def get_app_context(app: Module, user=None, team=None):
    variable_service = get_variable_service()
    return AppContext(
        user=user,
        team=team,
        variables=await variable_service.make_variable_set(user=user, team=await user.team if user else None, app=app),
        app_name=app.name,
        routing_keys=await Eventory.make_routing_keys_set(app=app)
    )
