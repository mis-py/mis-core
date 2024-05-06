import aiohttp
from loguru import logger
from ujson import loads, JSONDecodeError
import urllib3
import re

from services.modules.context import AppContext
from services.variables.variable_set import VariableSet
from core.utils.notification.message import Message
from services.eventory import Eventory

from ..service import (
    ReplacementGroupService,
    ProxyDomainService
)


async def proxy_change(ctx: AppContext, replacement_group_ids: list[int]):
    """ Function to manually run domain replacement for specific replacement groups """

    # Gather active replacement groups data that we will use along with tracker instance data
    groups = await ReplacementGroupService().filter(
        id__in=replacement_group_ids,
        is_active=True,
        prefetch_related=['tracker_instance']
    )

    # TODO verify it
    if not groups:
        logger.error(
            f"Run replacement_group_proxy_change task ERROR: Group ids: {replacement_group_ids} not exists or not active")
        return

    await ProxyDomainService().change_domain(groups, ctx)
