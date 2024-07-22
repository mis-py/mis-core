from abc import ABC, abstractmethod
from urllib.parse import urlparse

from ujson import loads, JSONDecodeError

import aiohttp
import urllib3
from loguru import logger

from core.services.base.base_service import BaseService
from modules.binom_companion.db.models import TrackerInstance, ReplacementGroup, ProxyDomain, TrackerType
from modules.binom_companion.repository import TrackerInstanceRepository
from modules.binom_companion.services.keitaro import KeitaroAPI
from modules.binom_companion.util.util import regexp_match


class Tracker(ABC):
    @abstractmethod
    async def check_connection(self, tracker_instance: TrackerInstance):
        pass

    @abstractmethod
    async def fetch_offers(self, group: ReplacementGroup, instance: TrackerInstance):
        pass

    @abstractmethod
    async def fetch_landings(self, group: ReplacementGroup, instance: TrackerInstance):
        pass

    @abstractmethod
    async def change_offers_domain(self, offer_ids, new_domain: ProxyDomain, instance: TrackerInstance) -> str:
        pass

    @abstractmethod
    async def change_landings_domain(self, landings_ids, new_domain: ProxyDomain, instance: TrackerInstance) -> str:
        pass


class BinomInstanceService(BaseService, Tracker):
    def __init__(self):
        super().__init__(repo=TrackerInstanceRepository(model=TrackerInstance))

    async def check_connection(self, tracker_instance: TrackerInstance):

        async with aiohttp.ClientSession() as session:
            url = f"{tracker_instance.base_url}/{tracker_instance.edit_route}?api_key={tracker_instance.api_key}&action=monitor@get"

            response = await session.get(url)

            if not response.ok:
                logger.error(
                    f'Invalid response from Tracker {tracker_instance.name}: {response.status} {response.text}')
                return None

            try:
                data = await response.json(loads=loads, content_type=None)

            except JSONDecodeError:
                logger.error(f'Invalid data from Tracker {tracker_instance.name}: {response.text}')
                return None

            if data and len(data) > 0:
                return data.get("tracker_info")
        return None

    @staticmethod
    async def make_tracker_get_request(
            instance: TrackerInstance,
            page: str,
            group: str = 'all',
            networks_filter: str = 'all'
    ):
        """
        Typical get request must return array with some objects
        """

        async with aiohttp.ClientSession() as session:
            url = f"{instance.base_url}/{instance.get_route}?page={page}&user_group=all" \
                  f"&status=1&group={group}&networks_filter={networks_filter}" \
                  f"&date=3&api_key={instance.api_key}"
            # logger.debug(url)
            response = await session.get(url)
            # logger.debug(await response.json(content_type='text/html'))
            if not response.ok:
                logger.error(f'Invalid response from Tracker {instance.name}: {response.status} {response.text}')
                return None

            try:
                data = await response.json(loads=loads, content_type=None)
            except JSONDecodeError:
                logger.error(f'Invalid data from Tracker {instance.name}: {response.text}')
                return None

            if not isinstance(data, list):
                logger.error(f'Got non-array data from Tracker {instance.name}: {data=}')
                return None

            return await response.json(content_type='text/html')

    @staticmethod
    async def make_tracker_post_request(
            instance: TrackerInstance,
            payload: dict,
            action: str,
    ):
        async with aiohttp.ClientSession() as session:
            url = f"{instance.base_url}/{instance.edit_route}"

            payload = {
                "api_key": instance.api_key,
                "action": action,
                "payload": payload
            }
            # logger.debug(url)
            # logger.debug(payload)
            response = await session.post(url, json=payload)

            return await response.json(content_type='text/html')

    async def fetch_offers(self, group: ReplacementGroup, instance: TrackerInstance):
        offer_ids = []
        domains = set()

        json_data = await self.make_tracker_get_request(
            instance=instance,
            page='Offers',
            group=group.offer_group_id
        )

        if not json_data:
            return offer_ids, list(domains)

        if group.offer_geo:
            json_data = [item for item in json_data if item.get('geo').lower() == group.offer_geo.lower()]

        if group.offer_name_regexp_pattern:
            json_data = [
                item for item in json_data if regexp_match(item.get('name').lower(), group.offer_name_regexp_pattern)
            ]

        for off in json_data:
            offer_ids.append(off.get('id'))
            domain = urllib3.util.parse_url(off.get('url')).host
            if domain:
                domains.add(domain)

        return offer_ids, list(domains)

    async def fetch_landings(self, group: ReplacementGroup, instance: TrackerInstance):
        landing_ids = []
        domains = set()

        json_data = await self.make_tracker_get_request(
            instance=instance,
            page='Landing_page',
            group=group.land_group_id
        )

        if not json_data:
            return landing_ids, list(domains)

        if group.land_language:
            json_data = [item for item in json_data if item.get('lang').lower() == group.land_language.lower()]

        if group.land_name_regexp_pattern:
            json_data = [item for item in json_data if regexp_match(item.get('name'), group.land_name_regexp_pattern)]

        for land in json_data:
            landing_ids.append(land.get('id'))
            domain = urllib3.util.parse_url(land.get('url')).host
            if domain:
                domains.add(domain)

        return landing_ids, list(domains)

    async def change_offers_domain(self, offer_ids, new_domain: ProxyDomain, instance: TrackerInstance) -> str:
        if not offer_ids:
            return ""

        json_data = await self.make_tracker_post_request(
            instance=instance,
            action="offer@mass_edit",
            payload={
                "options": {
                    "domain": new_domain.name,
                },
                "offers": offer_ids,
            }
        )

        return json_data

    async def change_landings_domain(self, landings_ids, new_domain: ProxyDomain, instance: TrackerInstance) -> str:
        if not landings_ids:
            return ""

        json_data = await self.make_tracker_post_request(
            instance=instance,
            action="landing@mass_edit",
            payload={
                "options": {
                    "domain": new_domain.name,
                },
                "landings": landings_ids,
            }
        )

        return json_data


class KeitaroInstanceService(BaseService, Tracker):
    def __init__(self):
        super().__init__(repo=TrackerInstanceRepository(model=TrackerInstance))

    async def check_connection(self, tracker_instance: TrackerInstance):
        keitaro = KeitaroAPI(base_url=tracker_instance.base_url, api_key=tracker_instance.api_key)
        return await keitaro.check()

    async def fetch_offers(self, group: ReplacementGroup, instance: TrackerInstance):
        keitaro = KeitaroAPI(base_url=instance.base_url, api_key=instance.api_key)
        offers = await keitaro.get_offers()

        filtered_offers = self._filter_offers(offers=offers, group=group)

        offer_ids, domains = [], []
        for offer in filtered_offers:
            offer_ids.append(str(offer['id']))
            domain = self._extract_domain(offer['action_payload'])
            domains.append(domain)

        return offer_ids, domains

    async def fetch_landings(self, group: ReplacementGroup, instance: TrackerInstance):
        keitaro = KeitaroAPI(base_url=instance.base_url, api_key=instance.api_key)
        landings = await keitaro.get_landings()

        filtered_landings = self._filter_landings(landings=landings, group=group)

        landing_ids, domains = [], []
        for landing in filtered_landings:
            landing_ids.append(str(landing['id']))
            domain = self._extract_domain(landing['action_payload'])
            domains.append(domain)

        return landing_ids, domains

    async def change_offers_domain(self, offer_ids, new_domain: ProxyDomain, instance: TrackerInstance) -> list:
        keitaro = KeitaroAPI(base_url=instance.base_url, api_key=instance.api_key)
        responses = []
        for offer_id in offer_ids:
            offer_data = await keitaro.get_offer(offer_id)
            old_domain = self._extract_domain(offer_data['action_payload'])
            action_payload = offer_data['action_payload'].replace(old_domain, new_domain.name, 1)
            payload = {'action_payload': action_payload}

            response = await keitaro.update_offer(offer_id=offer_id, payload=payload)
            responses.append(response)
        return responses

    async def change_landings_domain(self, landing_ids, new_domain: ProxyDomain, instance: TrackerInstance) -> list:
        keitaro = KeitaroAPI(base_url=instance.base_url, api_key=instance.api_key)
        responses = []
        for landing_id in landing_ids:
            landing_data = await keitaro.get_landing(landing_id)
            old_domain = self._extract_domain(landing_data['action_payload'])
            action_payload = landing_data['action_payload'].replace(old_domain, new_domain.name, 1)
            payload = {'action_payload': action_payload}

            response = await keitaro.update_landing(landing_id=landing_id, payload=payload)
            responses.append(response)
        return responses

    def _filter_offers(self, offers: list[dict], group: ReplacementGroup) -> list[dict]:
        filtered_offers = []
        for offer in offers:
            if group.offer_group_id and offer['group_id'] != group.offer_group_id:
                continue
            elif group.offer_geo and group.offer_geo not in offer['country']:
                continue
            elif group.offer_name_regexp_pattern and not regexp_match(input_text=offer['name'],
                                                                      regexp=group.offer_name_regexp_pattern):
                continue
            filtered_offers.append(offer)
        return filtered_offers

    def _filter_landings(self, landings: list[dict], group: ReplacementGroup) -> list[dict]:
        filtered_landings = []
        for landing in landings:
            if group.land_group_id and landing['group_id'] != group.land_group_id:
                continue
            elif group.land_name_regexp_pattern and not regexp_match(input_text=landing['name'],
                                                                     regexp=group.land_name_regexp_pattern):
                continue
            filtered_landings.append(landing)
        return filtered_landings

    def _extract_domain(self, url: str):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return domain


def get_tracker_service(tracker_type: TrackerType) -> Tracker:
    tracker_services = {
        TrackerType.BINOM: BinomInstanceService(),
        TrackerType.KEITARO: KeitaroInstanceService(),
    }
    return tracker_services[tracker_type]
