import aiohttp
from loguru import logger


class KeitaroAPI:
    API_URL = '/admin_api/v1'
    OFFERS_URL = API_URL + '/offers'
    LANDING_URL = API_URL + '/landing_pages'

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = self.make_auth_headers()

    def make_auth_headers(self):
        return {'Api-Key': self.api_key}

    async def check(self):
        url = self.base_url + self.OFFERS_URL
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"Tracker GET '{url}' error: {text}")
                    return {'status': False, 'message': text}

                return {'status': True, 'message': 'Ok'}


    async def make_get_request(self, endpoint_url: str):
        url = self.base_url + endpoint_url
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    logger.error(f"Tracker GET '{endpoint_url}' error: {await response.text()}")
                    return None

                response_json = await response.json()
                return response_json

    async def make_put_request(self, endpoint_url: str, payload: dict):
        url = self.base_url + endpoint_url
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=payload, headers=self.headers) as response:
                if response.status != 200:
                    logger.error(f"Tracker PUT '{endpoint_url}' payload {payload} error: {await response.text()}")
                    return None

                response_json = await response.json()
                return response_json

    async def get_offers(self):
        return await self.make_get_request(endpoint_url=self.OFFERS_URL)

    async def get_offer(self, offer_id: int):
        endpoint_url = self.OFFERS_URL + f'/{offer_id}'
        return await self.make_get_request(endpoint_url=endpoint_url)

    async def update_offer(self, offer_id: int, payload: dict):
        endpoint_url = self.OFFERS_URL + f'/{offer_id}'
        return await self.make_put_request(endpoint_url=endpoint_url, payload=payload)

    async def get_landings(self):
        return await self.make_get_request(endpoint_url=self.LANDING_URL)

    async def get_landing(self, landing_id: int):
        endpoint_url = self.LANDING_URL + f'/{landing_id}'
        return await self.make_get_request(endpoint_url=endpoint_url)

    async def update_landing(self, landing_id: int, payload: dict):
        endpoint_url = self.LANDING_URL + f'/{landing_id}'
        return await self.make_put_request(endpoint_url=endpoint_url, payload=payload)
