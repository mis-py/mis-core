from abc import ABC, abstractmethod

from libs.ws_manager import WSManager
from libs.ws_manager.enums import Action, ResponseStatus


class ActionHandler(ABC):
    @abstractmethod
    async def handle(self, user_id: int, input_data: dict):
        raise NotImplementedError


class SubscribeHandler(ActionHandler):
    """Subscribe user to event"""

    async def handle(self, user_id, input_data: dict):
        event = input_data.get('event')
        if not event:
            await WSManager.send_answer(
                message_data={'message': "Subscribe failed. No 'event' provided"},
                user_id=user_id,
                action=Action.SUBSCRIBE,
                status=ResponseStatus.ERROR,
            )
            return

        WSManager.subscribe(user_id, event=event)
        await WSManager.send_answer(
            message_data={'message': f"Success '{event}' event subscribe"},
            user_id=user_id,
            action=Action.SUBSCRIBE,
            status=ResponseStatus.SUCCESS,
        )


class UnsubscribeHandler(ActionHandler):
    """Unsubscribe user from event"""

    async def handle(self, user_id, input_data: dict):
        event = input_data.get('event')
        if not event:
            await WSManager.send_answer(
                message_data={'message': "Unsubscribe failed. No action field"},
                user_id=user_id,
                action=Action.UNSUBSCRIBE,
                status=ResponseStatus.ERROR,
            )
            return

        WSManager.unsubscribe(user_id, event=event)
        await WSManager.send_answer(
            message_data={'message': f"Success '{event}' event unsubscribe"},
            user_id=user_id,
            action=Action.UNSUBSCRIBE,
            status=ResponseStatus.SUCCESS,
        )


def make_action_handler(action: str) -> ActionHandler:
    factory_handlers = {
        Action.SUBSCRIBE: SubscribeHandler(),
        Action.UNSUBSCRIBE: UnsubscribeHandler(),
    }
    return factory_handlers.get(action)
