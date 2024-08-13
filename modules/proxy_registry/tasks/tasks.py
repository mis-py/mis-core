import urllib3
import aiohttp
from loguru import logger
from datetime import datetime, timedelta

from core.utils.module.components import ScheduledTasks
from core.utils.app_context import AppContext
from core.utils.notification.eventory import eventory_publish

from libs.redis import RedisService
from modules.proxy_registry.config import RoutingKeys
from modules.proxy_registry.dependencies.services import get_proxy_service
from modules.proxy_registry.services.util import change_proxy_ip, check_proxy_id_by_ipify

urllib3.disable_warnings()

scheduled_tasks = ScheduledTasks()
routing_keys = RoutingKeys()


# this task change proxy IP every N hours
@scheduled_tasks.schedule_task(hours=1, start_date=datetime.now() + timedelta(seconds=30))
async def change_proxies_ip(ctx: AppContext, **kwargs):
    proxy_service = get_proxy_service()
    proxies = await proxy_service.filter(change_url__startswith='http', is_enabled=True)

    for proxy in proxies:
        result = await change_proxy_ip(proxy, RedisService())

        # TODO status maaybe 200 but actual IP of proxy can be the same due to error \
        #   so we need to implement compare actual public IP before and after call proxy change url
        if result['status'] == 200:
            logger.debug(f"[{proxy.name}] IP changed! Result: {result['text']}")
            await eventory_publish(
                body={'proxy_name': proxy.name, 'status': result['status'], 'text': result['text']},
                routing_key=routing_keys.PROXY_IP_CHANGED,
                channel_name=ctx.app_name,
            )
        else:
            logger.error(f"[{proxy.name}] Failed to change IP! Result: {result['text']}")
            await eventory_publish(
                body={'proxy_name': proxy.name, 'status': result['status'], 'text': result['text']},
                routing_key=routing_keys.PROXY_IP_FAILED,
                channel_name=ctx.app_name,
            )


@scheduled_tasks.schedule_task(minutes=15, start_date=datetime.now() + timedelta(seconds=30))
async def proxy_self_check(ctx: AppContext, **kwargs):
    proxy_service = get_proxy_service()
    proxies = await proxy_service.filter(is_enabled=True)

    for proxy in proxies:
        result = await check_proxy_id_by_ipify(proxy, RedisService())

        proxy_up = result['status'] == 200
        proxy_changed = proxy_up != proxy.is_online

        if proxy_changed:
            if proxy_up:
                logger.debug(f"[{proxy.name}] Proxy is online! Result: {result['text']}")
                await eventory_publish(
                    body={'proxy_name': proxy.name, 'status': result['status'], 'text': result['text']},
                    routing_key=routing_keys.PROXY_STATUS_UP,
                    channel_name=ctx.app_name,
                )
            else:
                logger.error(f"[{proxy.name}] Proxy is down! Result: {result['text']} Exceptions: {', '.join([str(e) for e in result['exceptions']])}")
                await eventory_publish(
                    body={'proxy_name': proxy.name, 'status': result['status'], 'text': result['text']},
                    routing_key=routing_keys.PROXY_STATUS_DOWN,
                    channel_name=ctx.app_name,
                )

            proxy.is_online = proxy_up
            await proxy.save()
