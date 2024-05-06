from typing import Annotated
from fastapi import Depends
from services.variables.variable_set import VariableSet
from core.dependencies.security import get_current_user
from core.dependencies.misc import get_current_app
from services.variables.variables import VariablesManager


async def get_variable_set(
    user=Depends(get_current_user),
    module=Depends(get_current_app)
):
    return await VariablesManager.make_variable_set(user=user,team=await user.team, app=module)


VariablesDep = Annotated[VariableSet, Depends(get_variable_set)]