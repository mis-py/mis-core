import json
from enum import Enum

import loguru
from loguru import logger

from core.db.models import User
# from core.utils.notification import IncomingProcessedMessage
from core.utils.common import get_log_levels_above

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .sockets import WSManager


class Action(str, Enum):
    LOGS = 'logs'
    NOTIFICATIONS = 'notifications'


async def send_log_to_subscribers(ws_manager: 'WSManager', message: str):
    action = Action.LOGS.value
    message_data = json.loads(message)

    copied_connections = ws_manager.connections.copy()
    for user_id, connection in copied_connections.items():
        if not ws_manager.is_user_subscribed(user_id, action):
            continue

        extra = ws_manager.get_user_subscriptions(user_id)[action]
        level = extra.get('level')
        if level and level in loguru.logger._core.levels:
            above_levels = get_log_levels_above(level)
            if message_data['record']['level']['name'] not in above_levels:
                continue

        try:
            await ws_manager.send_action_message(connection['websocket'], message_data, action)
        except Exception:
            ws_manager.disconnect(user_id)


async def send_notification_to_subscribers(
        ws_manager: 'WSManager',
        message: IncomingProcessedMessage,
        users: list[User],
        # redis: RedisService,
):
    action = Action.NOTIFICATIONS.value
    message_data = message.to_dict()
    for user in users:
        if user.id not in ws_manager.connections:
            continue

        if not ws_manager.is_user_subscribed(user.id, action):
            continue

        try:
            connection = ws_manager.connections[user.id]['websocket']
            await ws_manager.send_action_message(connection, message_data, action)
        except Exception as error:
            ws_manager.disconnect(user.id)
            logger.warning(f"{error.__class__.__name__} {user.id} disconnected")
