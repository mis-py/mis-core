from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from core.db import User
from core.dependencies import get_current_user
from core.exceptions import AuthError

from .schema import AccessToken, ChangePasswordData
from core.security.auth_backend import create_access_token

router = APIRouter()


@router.post("/token", response_model=AccessToken)
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.authenticate(form_data.username, form_data.password)
    if not user:
        raise AuthError("Incorrect username or password")
    user.signed_in = True
    await user.save()

    access_token = create_access_token(user.username)
    return AccessToken(
        access_token=access_token,
        bearer="bearer",
        user_id=user.id,
        username=user.username
    )


@router.post("/logout")
async def logout(
        current_user: User = Depends(get_current_user),
):
    current_user.signed_in = False
    await current_user.save()
    return JSONResponse({
        'status': True
    })


@router.post("/change_password")
async def change_password(
        data: ChangePasswordData,
        current_user: User = Depends(get_current_user),
):
    result = await current_user.change_password(
        data.old_password, data.new_password
    )
    return JSONResponse({
        'status': result
    })
