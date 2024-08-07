from json import JSONDecodeError

from loguru import logger
from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from fastapi.params import Depends

from core.db.models import User
from core.dependencies.security import ws_user_core_sudo
from libs.ws_manager import WSManager
from libs.ws_manager.action_handlers import factory_handlers, make_action_handler
from libs.ws_manager.enums import ResponseStatus, Action

router = APIRouter()


@router.websocket("")
async def websocket_endpoint(
        websocket: WebSocket,
        user: User = Depends(ws_user_core_sudo),
):
    await WSManager.connect(websocket, user_id=user.pk)

    try:
        while True:
            try:
                message = await websocket.receive_json()
                logger.debug(f"[Websocket] Received message from user (id={user.pk}) - {message}")
            except JSONDecodeError:
                await WSManager.send_answer(
                    message_data={'message': "Json decode error"},
                    user_id=user.pk,
                    action=Action.UNKNOWN,
                    status=ResponseStatus.ERROR,
                )
                continue
            except WebSocketDisconnect:
                break

            if not isinstance(message, dict):
                await WSManager.send_answer(
                    message_data={'message': "Invalid message type; please send json"},
                    user_id=user.pk,
                    action=Action.UNKNOWN,
                    status=ResponseStatus.ERROR,
                )
                continue

            input_action, input_data = message.get('action'), message.get('data')
            action_handler = make_action_handler(action=input_action)
            if not action_handler:
                await WSManager.send_answer(
                    message_data={'message': "Unknown request"},
                    user_id=user.pk,
                    action=Action.UNKNOWN,
                    status=ResponseStatus.ERROR,
                )
                continue

            await action_handler.handle(user_id=user.pk, input_data=input_data)

    except Exception as error:
        logger.exception(error)
        WSManager.disconnect(user.pk)
