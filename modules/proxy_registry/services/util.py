from ssl import SSLCertVerificationError, SSLError, cert_time_to_seconds
from datetime import datetime
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)
import re
import ipaddress
import logging
from datetime import timedelta
from aiohttp import ClientSession, ClientResponse
import asyncio
from yarl import URL
from aiohttp.helpers import BaseTimerContext
from aiohttp import RequestInfo
from aiohttp.connector import Connection
from aiohttp.tracing import Trace
import time
from aiohttp import ClientHttpProxyError, ClientProxyConnectionError, ClientResponseError
from loguru import logger
from aiohttp_socks import ProxyConnector, ProxyError, ProxyConnectionError, ProxyTimeoutError
from dataclasses import dataclass, field, asdict
from fake_useragent import UserAgent

from libs.redis import RedisService
from modules.proxy_registry.db.models import Proxy


@dataclass
class ProxyException:
    exception: str
    exception_text: str
    destination_domain: str
    proxy_address: str
    retry: int
    request_headers: dict
    response_status: int
    response_text: str


@dataclass
class FetchResult:
    status: int = field(default_factory=int)
    text: str = field(default_factory=str)
    exceptions: list[ProxyException] = field(default_factory=list[ProxyException])


# make GET request using specified proxy string
# return object with GET result
async def fetch_result(domain, proxy_address=None, verify_ssl=True, retries=3, sleep_time=2) -> FetchResult:
    result = FetchResult()
    ua = UserAgent()

    try:
        headers = {
            'User-Agent': ua.random
        }
        connector = ProxyConnector.from_url(proxy_address) if proxy_address else None

        session = ClientSession(connector=connector, headers=headers, response_class=ProxyResponse)

        async with session:
            for retry in range(0, retries):

                status = -1
                text = ""
                response_certificate = ""

                try:
                    # verify_ssl: disabling it make response.certificate to be empty
                    response = await session.get(domain, verify_ssl=verify_ssl, raise_for_status=True)

                    # in most cases this code is never triggers exception
                    if verify_ssl:
                        response_certificate = str(response.certificate)
                        check_ssl_domain(response.certificate)

                    result.status = status = response.status
                    result.text = text = await response.text('utf-8')

                    response.close()
                    break

                except (
                        SSLCertVerificationError,  # SSL certificate error or invalid
                        SSLError,                 # Invalid ssl implementation
                        ClientHttpProxyError,     # Proxy responds with status other than 200 OK on CONNECT request
                        ClientProxyConnectionError,  # Connection to proxy can not be established
                        ProxyConnectionError,  # Could not connect to proxy, possibly invalid host/port data
                        ProxyTimeoutError,     # Timeout in connection to proxy
                        ProxyError,            # Other proxy errors
                        ClientResponseError,   # Proxy is OK but dest host return not success status code,
                        Exception,             # All other exceptions during request
                ) as exception:
                    result.exceptions.append(ProxyException(
                        exception.__class__.__name__,
                        str(exception),
                        domain, proxy_address, retry, headers,
                        status, text
                    ))

                finally:
                    await asyncio.sleep(sleep_time)

    except Exception as exception:
        result.exceptions.append(ProxyException(
            exception.__class__.__name__,
            "Connector or Client session exception: " + str(exception),
            domain, proxy_address, 0, {}, -1, ""
        ))

    return result


# async def check_domain_with_proxy(domain, proxy_url, retries=3):
#     proxy_connector = ProxyConnector.from_url(proxy_url)
#
#     async with ClientSession(connector=proxy_connector, response_class=ProxyResponse) as session:
#         last_exception = None
#         for retry in range(0, retries):
#             try:
#                 async with session.get(f'https://{domain}/') as response:
#                     if not check_ssl_domain(response.certificate):
#                         # TODO check with expired cert
#                         return ssl.SSLCertVerificationError(f"{domain} - {response.certificate}")
#
#                     response_text = await response.text()
#
#                     if response_text != 'ok':
#                         return ValueError(f"{domain} - {response_text}")
#
#                     return None
#
#             except ssl.SSLError as e:
#                 return ssl.SSLError(f"{domain} - {e}")
#
#             except Exception as e:
#                 await asyncio.sleep(5)
#                 last_exception = e
#
#     return last_exception


# TODO recreate it to aiohttp with concurrency in case of long check time (function exists in binom_companion.utils)
async def is_domain_ok_by_proxy(domain: str, proxy: Proxy, check_string="ok") -> bool | None:
    start_time = time.time()
    response = await fetch_result(domain, proxy.address)

    if len(response.exceptions):
        logger.warning(f'[{domain}] {proxy.name}: {len(response.exceptions)} exceptions during request.')
        return False

    if check_string not in response.text:
        logger.warning(f'[{domain}] {proxy.name}: Response is not "ok" {response}')
        return False

    logger.info(f'[{domain}]: Proxy check passed! Verify took {round(time.time() - start_time, 2)}s')

    return True


async def store_last_ip_in_redis(proxy_id, result, redis: RedisService):
    ip_candidate = None

    match = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", result.text)
    if match:
        ip_candidate = match.group(0)

    try:
        ip_address = ipaddress.ip_address(ip_candidate)
        # store last scanned IP for 60 minutes
        await redis.cache.setex(
            cache_name="proxy:last_known_ip",
            key=proxy_id,
            value=ip_candidate,
            time=timedelta(minutes=60),
        )

        # if we found a correct ip return it directly in response.text
        result.text = ip_candidate

    except ValueError:
        logging.debug(f"Not contains an ip address: {result.text}")


async def restore_last_ip_from_redis(proxies, redis: RedisService) -> dict:
    cursor, keys = await redis.scan(match=f'proxy:last_known_ip:*')
    values = await redis.mget(keys)

    def convert_to_int(key):
        try:
            return int(key.replace('proxy:last_known_ip:', ''))
        except ValueError:
            return -1

    # keys = ['proxy:shit', 'proxy:<Proxy>', 'proxy:6', 'proxy:<Proxy>']
    # values = ['somehere', '{"last_known_ip": "{\\"status\\":\\"OK\\",\\"code\\":200,\\"new_ip\\":\\"128.124.9.92\\",\\"rt\\":\\"5.17\\",\\"proxy_id\\":147929}"}', '{"last_known_ip": "128.124.48.239"}', 'lolo']
    cached_proxy_data = dict(zip(map(convert_to_int, keys), values))

    for proxy in proxies:
        if proxy.id in cached_proxy_data:
            proxy.last_known_ip = cached_proxy_data[proxy.id]


# use it for check proxy IP and status
async def check_proxy_address_by_ipify(proxy_address) -> dict:
    if not proxy_address:
        return {
            'status': 500,
            'text': 'No proxy address',
            'exceptions': []
        }
    result = await fetch_result(f'https://api.ipify.org', proxy_address)
    return asdict(result)


async def check_proxy_id_by_ipify(proxy, redis: RedisService) -> dict:
    if not proxy.address:
        return {
            'status': 500,
            'text': 'No proxy address',
            'exceptions': []
        }
    result = await fetch_result(f'https://api.ipify.org', proxy.address)
    if result.status == 200:
        await store_last_ip_in_redis(proxy.id, result, redis)
    return asdict(result)


async def change_proxy_ip(proxy: Proxy, redis_service) -> dict:
    # in case changing ip certificate doesn't matter

    if not proxy.change_url:
        return {
            'status': 500,
            'text': 'No proxy change url',
            'exceptions': []
        }

    result = await fetch_result(proxy.change_url, verify_ssl=False)
    if result.status == 200:
        await store_last_ip_in_redis(proxy.id, result, redis_service)
    return asdict(result)


def check_ssl_domain(certificate):
    if not certificate:
        raise SSLCertVerificationError(f"No certificate present: {str(certificate)}")

    cert_timestamp = cert_time_to_seconds(certificate['notAfter'])

    expire_date = datetime.fromtimestamp(cert_timestamp)

    if not expire_date:
        raise SSLCertVerificationError(f"Certificate {str(certificate)} has no expire date")

    if expire_date < datetime.now():
        raise SSLCertVerificationError(f"Certificate {str(certificate)} expired: {expire_date}")


class ProxyResponse(ClientResponse):
    def __init__(self, method: str, url: URL, *, writer: "asyncio.Task[None]",
                 continue100: Optional["asyncio.Future[bool]"], timer: BaseTimerContext, request_info: RequestInfo,
                 traces: List["Trace"], loop: asyncio.AbstractEventLoop, session: "ClientSession") -> None:
        super().__init__(method, url, writer=writer, continue100=continue100, timer=timer, request_info=request_info,
                         traces=traces, loop=loop, session=session)

        self.certificate: Optional[Dict[str, Union[Tuple[Any, ...], int, str]]] = None

    async def start(self, connection: "Connection") -> "ClientResponse":
        if connection is not None and connection.transport is not None:
            self.certificate = connection.transport.get_extra_info('peercert')
        return await super().start(connection)