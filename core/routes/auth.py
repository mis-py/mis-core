from typing import Annotated

from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from core.db.models import User
from core.dependencies import get_current_user
from core.dependencies.misc import UnitOfWorkDep

from core.schemas.auth import AccessToken, ChangePasswordData
from core.services.auth import AuthService

router = APIRouter()


@router.post("/token", response_model=AccessToken)
async def get_access_token(
        uow: UnitOfWorkDep,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    access_token = await AuthService(uow).authenticate(form_data)
    return access_token


@router.post("/logout")
async def logout(
        uow: UnitOfWorkDep,
        current_user: User = Depends(get_current_user),
):
    result = await AuthService(uow).de_authenticate(current_user.pk)
    return JSONResponse({
        'status': result
    })


@router.post("/change_password")
async def change_password_endpoint(
        uow: UnitOfWorkDep,
        data: ChangePasswordData,
        current_user: User = Depends(get_current_user),
):
    result = await AuthService(uow).change_password(
        current_user,
        data.old_password,
        data.new_password
    )

    return JSONResponse({
        'status': result
    })
