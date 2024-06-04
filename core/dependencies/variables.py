from typing import Annotated

from fastapi import Depends

from core.dependencies.misc import get_current_app
from core.dependencies.security import get_current_user

from core.utils.variable_set import VariableSet
from .services import get_variable_service


async def get_variable_set(
    user=Depends(get_current_user),
    module=Depends(get_current_app),
    variable_service=Depends(get_variable_service)
) -> VariableSet:
    return await variable_service.make_variable_set(user=user, team=await user.team, app=module)
