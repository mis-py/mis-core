from tortoise import transactions

from core.auth_backend import set_password
from core.db.models import User
from core.exceptions import MISError, ValidationFailed
from core.repositories.team import ITeamRepository
from core.repositories.user import IUserRepository
from core.schemas.user import UserCreate, UserUpdate, UserSelfUpdate
from core.services.base.base_service import BaseService
from core.utils.notification.recipient import Recipient
from core.exceptions import NotFound, AlreadyExists


class UserService(BaseService):
    def __init__(self, user_repo: IUserRepository, team_repo: ITeamRepository):
        self.user_repo = user_repo
        self.team_repo = team_repo
        super().__init__(repo=user_repo)

    @transactions.atomic()
    async def create_with_pass(self, user_in: UserCreate) -> User:
        if user_in.team_id is not None:
            team = await self.team_repo.get(id=user_in.team_id)
            if not team:
                raise NotFound(f"Team id '{user_in.team_id}' not exist")

        user = await self.user_repo.get(username=user_in.username)
        if user is not None:
            raise AlreadyExists(f"User with username '{user_in.username}' already exists")

        new_user = User(
            username=user_in.username,
            team_id=user_in.team_id,
            position=user_in.position,
        )
        set_password(new_user, user_in.password)
        await self.user_repo.save(obj=new_user)

        return new_user

    async def update_user(self, id: int, schema_in: UserUpdate | UserSelfUpdate) -> User:
        update_data = schema_in.model_dump(exclude_unset=True)
        if id == 1 and set(update_data.keys()) != {'password'}:  # ADMIN cat update only password
            raise ValidationFailed("ADMIN user can't be updated")
        return await self.user_repo.update(pk=id, data=update_data)

    async def update_client_data(self, id: int, old_client_data: dict, new_client_data: dict) -> dict:
        client_data = {**old_client_data, **new_client_data}
        cleared_client_data = {key: value for key, value in client_data.items() if value is not None}
        await self.user_repo.update(pk=id, data={'client_data': cleared_client_data})
        return cleared_client_data

    async def update_with_password(self, user: User, schema_in: UserUpdate) -> User:
        user = await self.update_user(id=user.pk, schema_in=schema_in)
        if schema_in.password is not None:
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
