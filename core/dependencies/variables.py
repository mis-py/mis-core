from fastapi import Request
from services.variables.variables import VariablesManager


async def get_settings_proxy(request: Request):
    current_app = request.state.current_app
    try:
        current_user = request.state.current_user
    except AttributeError:
        current_user = None

    return await VariablesManager.make_variable_set(user=current_user, app=current_app)