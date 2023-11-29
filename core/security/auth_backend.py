from datetime import datetime, timedelta, timezone
from typing import Any, Union

from fastapi.params import Query
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from const import DEV_ENVIRONMENT, ENVIRONMENT
from config import CoreSettings
from core.db.crud import crud_user
from core.db.models import User
from core.exceptions import TokenError, AccessError

settings = CoreSettings()


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=settings.URL_ROOT_PATH + "/auth/token",
    auto_error=False,
    scopes={}
)
auth_disabled = []


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}

    if ENVIRONMENT == DEV_ENVIRONMENT:
        # in dev environment token never expires
        to_encode.pop("exp")

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def user_form_token(token: str) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise TokenError("Invalid token payload")
    except ExpiredSignatureError:
        raise TokenError("Token is expired")
    except JWTError:
        raise TokenError("Could not validate credentials")

    user = await crud_user.get(username=username)
    if user is None or not user.signed_in:
        raise TokenError("User deleted or logged out")
    return user


async def check_user_perm(user: User, scopes):
    if not scopes:
        return None

    granted_perms = await user.granted_permissions(scopes_list=True)
    if not set(scopes) & set(granted_perms):
        raise AccessError("Not enough permissions")


def authorization_disabled(route: APIRoute):
    auth_disabled.append(route)


async def ws_user_core_sudo(token: str = Query(...)):
    user = await user_form_token(token)
    await check_user_perm(user, ['core:sudo'])
    return user
