from typing import Type

from tortoise.transactions import in_transaction

from core.auth_backend import set_password
from core.db.models import User
from core.exceptions import ValidationFailed, MISError, TokenError
from core.repositories.user import UserRepository, IUserRepository
from core.schemas.user import UserCreate, UserUpdate
from core.services.base.base_service import BaseService
from core.utils.notification.recipient import Recipient
from services.variables.utils import type_convert


class UserService(BaseService):
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo
        super().__init__(repo=user_repo)

    async def create_with_pass(self, user_in: UserCreate) -> User:
        async with in_transaction():
            new_user = User(
                username=user_in.username,
                team_id=user_in.team_id,
                position=user_in.position,
            )
            set_password(new_user, user_in.password)
            await self.user_repo.save(obj=new_user)

        return new_user

    async def update_with_password(self, user: User, schema_in: UserUpdate) -> User:
        # TODO restrict admin(1) editing for .username, .disabled, .team properties
        user = await self.user_repo.update(pk=user.pk, data=schema_in.model_dump(exclude_unset=True))
        set_password(user, schema_in.password)
        await self.user_repo.save(obj=user)
        return user

    async def update_users_team(self, users_ids: list[int], team_id: int) -> None:
        await self.user_repo.update_list(update_ids=users_ids, data={'team_id': team_id})

    async def delete(self, **filters) -> None:
        if 'id' in filters and filters['id'] == 1:
            raise MISError("User with id '1' can't be deleted")
        await self.user_repo.delete(**filters)

    async def users_who_receive_message(
            self,
            routing_key: str,
            is_force_send: bool,
            recipient: Recipient,
    ):
        if not recipient and not is_force_send:
            return await self.user_repo.filter_by_subscription(routing_key=routing_key)

        if is_force_send and not recipient:
            return await self.user_repo.filter()

        if recipient.type == Recipient.Type.USER:
            query = await self.user_repo.filter_queryable(id=recipient.user_id)
        elif recipient.type == Recipient.Type.TEAM:
            query = await self.user_repo.filter_queryable(team_id=recipient.team_id)
        else:
            raise Exception(f'Recipient type {recipient.type} not exist or not implement')

        if is_force_send and recipient:
            return await query

        return await self.user_repo.filter_by_subscription(routing_key=routing_key, query=query)
