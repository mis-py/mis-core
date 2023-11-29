from string import Template

from loguru import logger

from core.db import RoutingKey


def body_verbose_by_template(body, template_string: str):
    """Format body dict to string using Template string"""
    if not template_string:
        return None

    try:
        template = Template(template_string)
        return template.substitute(body)
    except KeyError as error:
        logger.error(f"Wrong template string key: {error}")
        return None


async def get_or_set_routing_key_cache(cache, routing_key: str):
    cache_name = "routing_key"

    # get
    value = await cache.get_json(cache_name=cache_name, key=routing_key)
    if value:
        return value

    # set
    key_instance = await RoutingKey.get_or_none(name=routing_key)
    value = routing_key_to_dict(key_instance)
    await cache.set_json(
        cache_name=cache_name,
        key=routing_key,
        value=value,
    )
    return value


def routing_key_to_dict(instance: RoutingKey) -> dict:
    value = {
        "key_verbose": instance.key_verbose,
        "template": instance.template,
    }
    return value
