import aiohttp
from loguru import logger

from core.utils.app_context import AppContext
from core.utils.module.components import EventManager
from ..config import RoutingKeys
from ..schemas.consumers import DomainCheckFailed

routing_keys = RoutingKeys()
event_consumers = EventManager()


@event_consumers.add_consumer(routing_keys.DOMAIN_CHECK_FAILED)
async def domain_check_failed_notifier(ctx: AppContext, validated_body: DomainCheckFailed):
    logger.info(f'[{validated_body.checked_domain}] {validated_body.message}')
    text = (f"Checked domain: {validated_body.checked_domain}\n"
            f"Message error: {validated_body.message}")
    tg_bot_token = ctx.variables.NOTIFY_TG_BOT_TOKEN
    tg_chat_id = ctx.variables.NOTIFY_TG_CHAT_ID

    if tg_bot_token and tg_chat_id:
        await send_telegram_message(
            bot_token=tg_bot_token,
            chat_id=tg_chat_id,
            message=text,
        )


async def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                return await response.text()
