import re
import ssl
from datetime import datetime
from aiohttp import ClientSession, ClientResponse
import asyncio
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)
from yarl import URL
from aiohttp.helpers import BaseTimerContext
from aiohttp import RequestInfo
from aiohttp.connector import Connection
from aiohttp.tracing import Trace


class SSLResponse(ClientResponse):
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


def check_ssl_domain(certificate):
    if not certificate:
        return False

    cert_timestamp = ssl.cert_time_to_seconds(certificate['notAfter'])

    expire_date = datetime.fromtimestamp(cert_timestamp)

    if not expire_date:
        return False

    if expire_date < datetime.now():
        return False

    return True


def regexp_match(input_text, regexp):
    # pattern = re.compile(r"off[0-9]+\s-\s[a-zA-Z]+\s-\s[a-zA-Z]+\s-\s[A-Za-z0-9]+", re.IGNORECASE)
    pattern = re.compile(regexp, re.IGNORECASE)
    return pattern.match(input_text)
