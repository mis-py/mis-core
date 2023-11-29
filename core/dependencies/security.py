import ipaddress
import loguru
from fastapi import Depends, Header
from fastapi.security import SecurityScopes
from starlette.requests import Request
from core.db.crud import crud_user
from core.exceptions import AuthError
from config import CoreSettings
from core.security.auth_backend import oauth2_scheme, user_form_token, check_user_perm

settings = CoreSettings()


async def get_current_user(
        request: Request,
        security_scopes: SecurityScopes,
        x_real_ip: str = Header(None, include_in_schema=False),
        token: str = Depends(oauth2_scheme)
):
    if not settings.AUTHORIZATION_ENABLED:
        return await crud_user.get(id=1)

    if token:
        user = await user_form_token(token)
        await check_user_perm(user, security_scopes.scopes)
        return user

    host = ipaddress.ip_address(x_real_ip or request.client.host)
    loguru.logger.warning(f'Unauthorized request: {host}')
    raise AuthError('Unauthorized')
