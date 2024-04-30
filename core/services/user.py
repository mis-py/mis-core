from core.auth_backend import set_password
from core.db.models import User
from core.exceptions import MISError
from core.schemas.user import UserCreate, UserUpdate
from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork


class UserService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.user_repo)
        self.uow = uow

    async def create_with_pass(self, user_in: UserCreate) -> User:
        async with self.uow:
            new_user = User(
                username=user_in.username,
                team_id=user_in.team_id,
                position=user_in.position,
            )
            set_password(new_user, user_in.password)
            await self.uow.user_repo.save(obj=new_user)

        return new_user

    async def update_with_password(self, user: User, schema_in: UserUpdate) -> User:
        # TODO restrict admin(1) editing for .username, .disabled, .team properties
        user = await self.uow.user_repo.update(pk=user.pk, data=schema_in.model_dump(exclude_unset=True))
        set_password(user, schema_in.password)
        await self.uow.user_repo.save(obj=user)
        return user

    async def update_users_team(self, users_ids: list[int], team_id: int) -> None:
        await self.repo.update_list(update_ids=users_ids, data={'team_id': team_id})

    async def delete(self, **filters) -> None:
        if 'id' in filters and filters['id'] == 1:
            raise MISError("User with id '1' can't be deleted")
        await self.repo.delete(**filters)