from fastapi.security import OAuth2PasswordRequestForm

from core.auth_backend import create_access_token
from core.exceptions import AuthError, ValidationFailed
from core.schemas.auth import AccessToken
from core.services.base.unit_of_work import IUnitOfWork
from core.utils.security import verify_password, get_password_hash


class AuthService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def authenticate(self, form_data: OAuth2PasswordRequestForm) -> AccessToken:
        user = await self.uow.user_repo.get(username=form_data.username)

        if not user or not verify_password(form_data.password, user.hashed_password):
            raise AuthError("Incorrect username or password")

        # set status signed_in True
        await self.uow.user_repo.update(id=user.pk, data={'signed_in': True})

        access_token = create_access_token(user.username)
        return AccessToken(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            username=user.username
        )

    async def de_authenticate(self, user_id: int) -> bool:
        await self.uow.user_repo.update(id=user_id, data={'signed_in': False})
        return True

    async def change_password(self, user, old_password: str, new_password: str) -> bool:
        """
        Set new password for user only if old_password matches
        :param user: user model
        :param old_password: old plain password
        :param new_password: new plain password
        :return:
        """
        if not verify_password(old_password, user.hashed_password):
            raise ValidationFailed("Invalid old password")

        await self.uow.user_repo.update(
            id=user.pk,
            hashed_password=get_password_hash(new_password),
        )
        return True
