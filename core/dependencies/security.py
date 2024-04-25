import ipaddress
import loguru
from fastapi import Depends, Header
from fastapi.params import Query
from fastapi.security import SecurityScopes
from starlette.requests import Request

from core.dependencies.uow import UnitOfWorkDep
from core.exceptions import AuthError
from config import CoreSettings
from core.auth_backend import oauth2_scheme, check_user_perm
from core.services.auth import AuthService
from core.services.user import UserService

settings = CoreSettings()


async def get_current_user(
        uow: UnitOfWorkDep,
        request: Request,
        security_scopes: SecurityScopes,
        x_real_ip: str = Header(None, include_in_schema=False),
        token: str = Depends(oauth2_scheme),
):
    if not settings.AUTHORIZATION_ENABLED:
        return await UserService(uow).get(id=1)

    if token:
        user = await AuthService(uow).get_user_from_token(token=token)
        await check_user_perm(user, security_scopes.scopes)
        return user

    host = ipaddress.ip_address(x_real_ip or request.client.host)
    loguru.logger.warning(f'Unauthorized request: {host}')
    raise AuthError('Unauthorized')


async def ws_user_core_sudo(uow: UnitOfWorkDep, token: str = Query(...)):
    user = await AuthService(uow).get_user_from_token(token=token)
    await check_user_perm(user, ['core:sudo'])
    return user
