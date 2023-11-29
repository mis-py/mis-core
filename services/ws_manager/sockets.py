import time
from typing import Callable

from fastapi.websockets import WebSocket
from loguru import logger


class WSManager:
    # Hold client connections
    _connections: dict[int, dict] = {}
    _actions: dict = {}

    @classmethod
    async def connect(cls, websocket: WebSocket, user_id: int):
        await websocket.accept()
        cls._connections[user_id] = {
            'websocket': websocket,
            # Client can subscribe for various events here
            'subscribes': {},
        }
        logger.debug(f"[Websocket] User (id={user_id}) connected")

    @classmethod
    def disconnect(cls, user_id: int):
        del cls._connections[user_id]
        logger.debug(f"[Websocket] User (id={user_id}) disconnected")

    @classmethod
    def subscribe(cls, message: dict, user_id: int):
        action = message.pop('subscribe')
        if action not in cls._actions:
            return False
        cls._connections[user_id]['subscribes'][action] = {**message}
        return True

    @classmethod
    def unsubscribe(cls, message: dict, user_id: int):
        action = message.pop('unsubscribe')
        try:
            del cls._connections[user_id]['subscribes'][action]
            return True
        except KeyError:
            return False

    @classmethod
    def register_action(cls, action: str, callback: Callable):
        cls._actions[action] = callback

    @classmethod
    def get_user_subscriptions(cls, user_id: int):
        return cls._connections[user_id]['subscribes']

    @classmethod
    def is_user_subscribed(cls, user_id: int, action: str):
        if action in cls.get_user_subscriptions(user_id):
            return True
        return False

    @staticmethod
    async def send_action_message(connection: WebSocket, message: dict, action: str):
        data = {
            'action': action,
            'data': message,
            'time': int(time.time()),
        }
        await connection.send_json(data)

    @classmethod
    async def run_action(cls, action: str, *args, **kwargs):
        await cls._actions[action](cls, *args, **kwargs)
