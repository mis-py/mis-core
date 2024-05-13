from tortoise.exceptions import IntegrityError

from core.auth_backend import set_password
from core.db.models import User
from core.exceptions import ValidationFailed, MISError, TokenError
from core.schemas.user import UserCreate, UserUpdate
from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork
from core.services.team import TeamService
from core.utils.notification.recipient import Recipient
from core.exceptions import NotFound, AlreadyExists


class UserService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.user_repo)
        self.uow = uow

    async def create_with_pass(self, user_in: UserCreate) -> User:
        if user_in.team_id is not None:
            team = await TeamService(self.uow).get(id=user_in.team_id)
            if not team:
                raise NotFound(f"Team id '{user_in.team_id}' not exist")

        async with self.uow:
            # TODO refactor this try except shit
            try:
                new_user = User(
                    username=user_in.username,
                    team_id=user_in.team_id,
                    position=user_in.position,
                )
                set_password(new_user, user_in.password)
                await self.uow.user_repo.save(obj=new_user)
            except IntegrityError:
                raise AlreadyExists(f"User with username '{user_in.username}' already exists")

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

    async def users_who_receive_message(
            self,
            routing_key: str,
            is_force_send: bool,
            recipient: Recipient,
    ):
        if not recipient and not is_force_send:
            return await self.uow.user_repo.filter_by_subscription(routing_key=routing_key)

        if is_force_send and not recipient:
            return await self.uow.user_repo.filter()

        if recipient.type == Recipient.Type.USER:
            query = await self.uow.user_repo.filter_queryable(id=recipient.user_id)
        elif recipient.type == Recipient.Type.TEAM:
            query = await self.uow.user_repo.filter_queryable(team_id=recipient.team_id)
        else:
            raise Exception(f'Recipient type {recipient.type} not exist or not implement')

        if is_force_send and recipient:
            return await query

        return await self.uow.user_repo.filter_by_subscription(routing_key=routing_key, query=query)
