import asyncio
import aiohttp
from loguru import logger
from ujson import loads, JSONDecodeError
import urllib3
import re

from ..db.models import (
    ReplacementGroup,
    TrackerInstance
)

# TODO move it to core common utils
def safe_unpack(iterable: list, n: int):
    for row in iterable:
        row.extend([None] * (n - len(row)))
        yield row[:n]


async def gather_with_concurrency(n, *coros):
    semaphore = asyncio.Semaphore(n)

    async def sem_coro(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*(sem_coro(c) for c in coros), return_exceptions=True)


# clamp value between two numbers
def clamp(number, min_value=0.0, max_value=1.0):
    return round(float(max(min(max_value, number), min_value)), 2)


def regexp_match(input_text, regexp):
    # pattern = re.compile(r"off[0-9]+\s-\s[a-zA-Z]+\s-\s[a-zA-Z]+\s-\s[A-Za-z0-9]+", re.IGNORECASE)
    pattern = re.compile(regexp, re.IGNORECASE)
    return pattern.match(input_text)


async def fetch_offers(group: ReplacementGroup, instance: TrackerInstance):
    offer_ids = []
    domains = set()

    async with aiohttp.ClientSession() as session:
        for aff_network_id in group.aff_networks_ids:
            url = f"{instance.base_url}?page=Offers&user_group=all" \
                  f"&status=1&group={group.offer_group_id or 'all'}&networks_filter={aff_network_id}" \
                  f"&date=3&api_key={instance.api_key}"

            response = await session.get(url)

            if not response.ok:
                logger.error(f'Invalid response from Tracker {instance.name}: {response.status} {response.text}')
                return offer_ids, list(domains)

            try:
                data = await response.json(loads=loads, content_type=None)
            except JSONDecodeError:
                logger.error(f'Invalid data from Tracker {instance.name}: {response.text}')
                return offer_ids, list(domains)

            if not isinstance(data, list):
                logger.error(f'Got non-array data from Tracker {instance.name}: {data=}')
                return offer_ids, list(domains)

            json_data = await response.json(content_type='text/html')

            filtered_geo = filter(lambda x: x['geo'].lower() == group.offer_geo.lower(), json_data)

            filtered_names = filter(
                lambda x: regexp_match(x['name'].lower(), group.offer_name_regexp_pattern), filtered_geo
            )

            for off in filtered_names:
                offer_ids.append(off.get('id'))
                domain = urllib3.util.parse_url(off.get('url')).host
                domains.add(domain)

    return offer_ids, list(domains)


async def fetch_landings(group: ReplacementGroup, instance: TrackerInstance):
    landing_ids = []
    domains = set()

    async with aiohttp.ClientSession() as session:
        url = f"{instance.base_url}?page=Landing_page&user_group=all" \
              f"&status=1&group={group.land_group_id}" \
              f"&date=1&api_key={instance.api_key}"

        response = await session.get(url)

        if not response.ok:
            logger.error(f'Invalid response from Tracker {instance.name}: {response.status} {response.text}')
            return landing_ids, list(domains)

        try:
            data = await response.json(loads=loads, content_type=None)
        except JSONDecodeError:
            logger.error(f'Invalid data from Tracker {instance.name}: {response.text}')
            return landing_ids, list(domains)

        if not isinstance(data, list):
            logger.error(f'Got non-array data from Tracker {instance.name}: {data=}')
            return landing_ids, list(domains)

        json_data = await response.json(content_type='text/html')

        lang_filtered = filter(lambda x: x['lang'].lower() == group.land_language.lower(), json_data)

        name_filtered = filter(lambda x: regexp_match(x['name'], group.land_name_regexp_pattern), lang_filtered)

        for land in name_filtered:
            landing_ids.append(land.get('id'))
            domain = urllib3.util.parse_url(land.get('url')).host
            domains.add(domain)

    return landing_ids, list(domains)


async def change_offers_domain(offer_ids, new_domain, instance: TrackerInstance) -> str:
    async with aiohttp.ClientSession() as session:
        payload = {
            "api_key": instance.api_key,
            "action": "offer@mass_edit",
            "payload": {
                "options": {
                    "domain": new_domain,
                },
                "offers": offer_ids,
            }
        }

        if not offer_ids:
            logger.debug(f'No offers to change')
            return ""

        response = await session.post(instance.edit_route, json=payload)
        json_data = await response.json(content_type='text/html')
        logger.debug(f'Changing offers domains. New domain: {new_domain}, result: {json_data}, offers: {offer_ids}')
        return json_data


async def change_landings_domain(landings_ids, new_domain, instance: TrackerInstance) -> str:
    async with aiohttp.ClientSession() as session:
        payload = {
            "api_key": instance.api_key,
            "action": "landing@mass_edit",
            "payload": {
                "options": {
                    "domain": new_domain,
                },
                "landings": landings_ids,
            }
        }

        if not landings_ids:
            logger.debug(f'No landings to change')
            return ""

        response = await session.post(instance.edit_route, json=payload)
        json_data = await response.json(content_type='text/html')
        logger.debug(
            f'Changing landing domains. New domain: {new_domain}, result: {json_data}, landings: {landings_ids}')
        return json_data
