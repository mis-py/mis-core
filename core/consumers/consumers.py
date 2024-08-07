from aio_pika import IncomingMessage

from core.dependencies.routing_key_service import get_routing_key_service, get_notificator_service
from core.dependencies.services import get_user_service
from core.utils.notification.message import EventMessage
from core.utils.module.components import EventManager
from core.utils.app_context import AppContext

core_event_consumers = EventManager()


@core_event_consumers.add_consumer('#')
async def all_events_notification(ctx: AppContext, message: EventMessage, incoming_message: IncomingMessage):
    if message.data_type == EventMessage.Data.INTERNAL:
        # internal events not for users notifications
        return

    # get event recipients
    user_service = get_user_service()
    users_recipients = await user_service.users_who_receive_message(
        routing_key=incoming_message.routing_key,
        recipient=message.recipient,
    )

    # make verbose text from rk template
    routing_key_service = get_routing_key_service()
    rk_object = await routing_key_service.get(name=incoming_message.routing_key)
    body_verbose = await routing_key_service.body_verbose_by_template(
        body=message.body,
        template_string=rk_object.template,
    )

    # send event notifications via websockets
    notificator_service = get_notificator_service()
    await notificator_service.ws_notify_users(
        message_data={
            'body': message.body,
            'body_verbose': body_verbose,
        },
        users=users_recipients
    )
