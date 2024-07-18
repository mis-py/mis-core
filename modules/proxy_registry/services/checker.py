import socket
from ssl import SSLError

import aiohttp
from aiohttp_socks import ProxyConnector
from loguru import logger

from modules.proxy_registry.exceptions import ProxyCheckError


class ProxyChecker:
    def __init__(self):
        self._current_ip = self._get_host_ip()

    async def check_proxy(self, proxy_url: str):
        connector = ProxyConnector.from_url(proxy_url)
        async with aiohttp.ClientSession(connector=connector) as proxy_session:
            try:
                ip = await self.check_ip_via_website(proxy_session)
            except Exception as e:
                logger.warning(e)
                return False

            if ip == self._current_ip:
                logger.error("Proxy IP equals server IP!")
                return False

        return True

    async def filter_valid_proxies(self, proxies: list[str]) -> list[str]:
        valid_proxies = []
        for proxy in proxies:
            is_valid = await self.check_proxy(proxy_url=proxy)
            if not is_valid:
                continue
            valid_proxies.append(proxy)
        return valid_proxies

    async def check_ip_via_website(self, proxy_session: aiohttp.ClientSession) -> str:
        website_check_callbacks = [self._get_ip_via_aws, self._get_ip_via_httpbin]

        for website_check in website_check_callbacks:
            try:
                return await website_check(proxy_session)
            except (ProxyCheckError, SSLError) as e:
                logger.warning(f"{website_check.__name__}: {e}")
                continue

        raise ProxyCheckError("All check websites failed!")

    @staticmethod
    def _get_host_ip():
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)

    @staticmethod
    async def _get_ip_via_httpbin(proxy_session: aiohttp.ClientSession) -> str:
        url = 'http://httpbin.org/ip'
        async with proxy_session.get(url) as response:
            if response.status != 200:
                raise ProxyCheckError(f"HTTPBIN status: {response.status}")

            data = await response.json()
            return data['origin']

    @staticmethod
    async def _get_ip_via_aws(proxy_session: aiohttp.ClientSession) -> str:
        url = 'https://checkip.amazonaws.com'
        async with proxy_session.get(url) as response:
            if response.status != 200:
                raise ProxyCheckError(f"WS status: {response.status}")

            text = await response.text()
            return text
