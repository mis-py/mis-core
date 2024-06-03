from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordBearer

from const import DEV_ENVIRONMENT, ENVIRONMENT
from config import CoreSettings
from core.db.models import User
from core.exceptions import AccessError, AuthError
from core.schemas.auth import AccessToken
from core.utils.security import verify_password, get_password_hash

settings = CoreSettings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=settings.ROOT_PATH + "/auth/token",
    auto_error=False,
    scopes={}
)
auth_disabled = []


async def authenticate(form_data) -> AccessToken:
    user = await User.get_or_none(username=form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise AuthError("Incorrect username or password")

    user.signed_in = True
    await user.save()

    access_token = create_access_token(user.username)
    return AccessToken(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username
    )


async def de_authenticate(user: User) -> bool:
    user.signed_in = False
    await user.save()
    return True


async def change_password(user, old_password, new_password) -> bool:
    """
    Set new password for user only if old_password matches
    :param user: user model
    :param old_password: old plain password
    :param new_password: new plain password
    :return:
    """
    if verify_password(old_password, user.hashed_password):
        set_password(user, new_password)
        await user.save()
        return True
    return False


def set_password(user, value):
    """
    Just set new password for user without verification
    :param user: user model
    :param value:
    :return:
    """

    user.hashed_password = get_password_hash(value)


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


async def check_user_perm(user: User, scopes):
    if not scopes:
        return None

    granted_perms = await user.get_granted_permissions(scopes_list=True)
    if not set(scopes) & set(granted_perms):
        raise AccessError("Not enough permissions")


def authorization_disabled(route: APIRoute):
    auth_disabled.append(route)
