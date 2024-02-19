from enum import Enum
from json import JSONDecodeError

from loguru import logger
from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from fastapi.params import Depends

from core.auth_backend import ws_user_core_sudo
from services.ws_manager import WSManager

router = APIRouter()


class ResponseStatus(str, Enum):
    OK = 'ok'
    ERROR = 'error'


@router.websocket("")
async def websocket_endpoint(
        websocket: WebSocket,
        user: str = Depends(ws_user_core_sudo),
):
    await WSManager.connect(websocket, user_id=user.id)
    try:
        while True:
            try:
                message = await websocket.receive_json()
                logger.debug(f"[Websocket] Received message from user (id={user.id}) - {message}")
            except JSONDecodeError:
                await websocket.send_json({
                    "status": ResponseStatus.ERROR,
                    "detail": "json decode error",
                })
                continue
            except WebSocketDisconnect:
                break

            if not isinstance(message, dict):
                await websocket.send_json({
                    "status": ResponseStatus.ERROR,
                    "detail": "error message type; please send json",
                })
                continue

            if message.get('subscribe'):
                is_subscribe = WSManager.subscribe(message, user.id)
                if is_subscribe:
                    await websocket.send_json({
                        "status": ResponseStatus.OK,
                        "detail": "subscribed",
                    })
                else:
                    await websocket.send_json({
                        "status": ResponseStatus.ERROR,
                        "detail": "failed subscribe",
                    })
            elif message.get('unsubscribe'):
                WSManager.unsubscribe(message, user.id)
                await websocket.send_json({
                    "status": ResponseStatus.OK,
                    "detail": "unsubscribed",
                })
            else:
                await websocket.send_json({
                    "status": ResponseStatus.ERROR,
                    "detail": "unknown request",
                })

    except Exception as error:
        logger.exception(error)
        WSManager.disconnect(user.id)
