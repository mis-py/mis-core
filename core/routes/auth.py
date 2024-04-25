from typing import Annotated

from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from core.db.models import User
from core.dependencies.security import get_current_user
from core.dependencies.uow import UnitOfWorkDep

from core.schemas.auth import AccessToken, ChangePasswordData
from core.services.auth import AuthService
from core.utils.schema import MisResponse

router = APIRouter()


@router.post(
    "/token",
    response_model=MisResponse[AccessToken]
)
async def get_access_token(
        uow: UnitOfWorkDep,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    access_token = await AuthService(uow).authenticate(form_data)
    return MisResponse[AccessToken](result=access_token)


@router.post(
    "/logout",
    response_model=MisResponse
)
async def logout(
        uow: UnitOfWorkDep,
        current_user: User = Depends(get_current_user),
):
    await AuthService(uow).de_authenticate(current_user.pk)
    return MisResponse()


@router.post(
    "/change_password",
    response_model=MisResponse
)
async def change_password_endpoint(
        uow: UnitOfWorkDep,
        data: ChangePasswordData,
        current_user: User = Depends(get_current_user),
):
    await AuthService(uow).change_password(
        current_user,
        data.old_password,
        data.new_password
    )

    return MisResponse()
