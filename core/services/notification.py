from tortoise.queryset import QuerySet

from core.db.models import RoutingKey, User
from core.crud import user
from core.utils.notification import Recipient
from core.crud.notification import subscription


async def subscribe_routing_key(user: User, routing_key: RoutingKey) -> None:
    await subscription.get_or_create_subscription(
        user=user, routing_key=routing_key
    )


async def unsubscribe_routing_key(user: User, routing_key: RoutingKey) -> None:
    await subscription.remove(user=user, routing_key=routing_key)


async def query_users_who_receive_message(routing_key: str, is_force_send: bool, recipient: Recipient) -> QuerySet:
    if not recipient and not is_force_send:
        return await user.query_get_by_subscription(routing_key)

    if is_force_send and not recipient:
        return await user.query_get_all()

    if recipient.type == Recipient.Type.USER:
        query = await user.query_get_multi(id=recipient.user_id)
    elif recipient.type == Recipient.Type.TEAM:
        query = await user.query_get_multi(team_id=recipient.team_id)
    else:
        raise Exception(f'Recipient type {recipient.type} not exist or not implement')

    if is_force_send and recipient:
        return query

    return await user.query_get_by_subscription(query=query, routing_key=routing_key)