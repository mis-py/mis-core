from typing import Annotated

from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm


from core.db.models import User
from core.dependencies import get_current_user


from core.schemas.auth import AccessToken, ChangePasswordData
from core.auth_backend import authenticate, de_authenticate, change_password

router = APIRouter()


@router.post("/token", response_model=AccessToken)
async def get_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    access_token = await authenticate(form_data)
    return access_token


@router.post("/logout")
async def logout(
        current_user: User = Depends(get_current_user),
):
    result = de_authenticate(current_user)

    return JSONResponse({
        'status': result
    })


@router.post("/change_password")
async def change_password_endpoint(
        data: ChangePasswordData,
        current_user: User = Depends(get_current_user),
):
    result = await change_password(
        current_user,
        data.old_password,
        data.new_password
    )

    return JSONResponse({
        'status': result
    })
