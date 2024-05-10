import ipaddress
from typing import Annotated

import loguru
from fastapi import Depends, Header
from fastapi.params import Query
from fastapi.security import SecurityScopes
from starlette.requests import Request

from core.dependencies.services import get_user_service, get_auth_service
from core.exceptions import AuthError
from config import CoreSettings
from core.auth_backend import oauth2_scheme, check_user_perm
from core.services.auth import AuthService
from core.services.user import UserService

settings = CoreSettings()


async def get_current_user(
        user_service: Annotated[UserService, Depends(get_user_service)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        request: Request,
        security_scopes: SecurityScopes,
        x_real_ip: str = Header(None, include_in_schema=False),
        token: str = Depends(oauth2_scheme),
):
    if not settings.AUTHORIZATION_ENABLED:
        # TODO replace it from config param
        return await user_service.get(username='admin')

    if token:
        user = await auth_service.get_user_from_token(token=token)
        await check_user_perm(user, security_scopes.scopes)

        if user.disabled:
            raise AuthError('User disabled')

        return user

    host = ipaddress.ip_address(x_real_ip or request.client.host)
    loguru.logger.warning(f'Unauthorized request: {host}')
    raise AuthError('Unauthorized')


async def ws_user_core_sudo(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        token: str = Query(...)):

    user = await auth_service.get_user_from_token(token=token)
    await check_user_perm(user, ['core:sudo'])
    return user
