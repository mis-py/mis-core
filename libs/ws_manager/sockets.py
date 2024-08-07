import time
from dataclasses import dataclass, field

from fastapi.websockets import WebSocket
from loguru import logger

from libs.ws_manager.enums import ResponseStatus, Action, WebsocketEvent


@dataclass
class Connection:
    user_id: int
    websocket: WebSocket

    # Client can subscribe for various events here
    subscribed_events: set[str] = field(default_factory=set)


class WSManager:
    # Hold client connections
    _connections: dict[int, Connection] = {}

    @classmethod
    async def connect(cls, websocket: WebSocket, user_id: int):
        await websocket.accept()
        cls._connections[user_id] = Connection(
            user_id=user_id,
            websocket=websocket,
        )
        logger.debug(f"[Websocket] User (id={user_id}) connected")

    @classmethod
    def disconnect(cls, user_id: int):
        del cls._connections[user_id]
        logger.debug(f"[Websocket] User (id={user_id}) disconnected")

    @classmethod
    def get_connection(cls, user_id: int) -> Connection:
        connection = cls._connections.get(user_id)
        if connection is None:
            raise ValueError(f"No connection for user (id={user_id}) found")
        return connection

    @classmethod
    def subscribe(cls, user_id: int, event: str):
        connection = cls.get_connection(user_id)
        connection.subscribed_events.add(event)

    @classmethod
    def unsubscribe(cls, user_id: int, event: str):
        connection = cls.get_connection(user_id)
        try:
            connection.subscribed_events.remove(event)
        except KeyError:
            # already removed or not exist; skip error
            pass

    @classmethod
    def is_subscribed_event(cls, user_id: int, event: str):
        connection = cls.get_connection(user_id)
        return event in connection.subscribed_events

    @classmethod
    def is_connection_exists(cls, user_id: int) -> bool:
        try:
            connection = cls.get_connection(user_id)
            return bool(connection)
        except ValueError:
            return False

    @classmethod
    async def _send_message(cls, websocket: WebSocket, data: dict):
        try:
            await websocket.send_json(data=data)
        except Exception as e:
            logger.warning(f'Send message error {e.__class__.__name__} {e}')

    @classmethod
    async def send_answer(cls, user_id: int, message_data: dict, action: Action, status: ResponseStatus):
        """This message send an answer to the user request"""
        connection = cls.get_connection(user_id)
        data = {
            'action': action,
            'data': message_data,
            'time': int(time.time()),
            'status': status,
        }
        await cls._send_message(websocket=connection.websocket, data=data)

    @classmethod
    async def send_event(cls, user_id: int, message_data: dict, event: WebsocketEvent):
        """This message send auto (ex: notification or log)"""
        connection = cls.get_connection(user_id)
        data = {
            'event': event,
            'data': message_data,
            'time': int(time.time()),
        }
        await cls._send_message(websocket=connection.websocket, data=data)
