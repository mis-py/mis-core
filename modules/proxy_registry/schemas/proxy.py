from typing import Literal

from core.utils.schema import MisModel


class ProxyBase(MisModel):
    name: str
    proxy_type: Literal['http', 'socks5'] = 'http'
    is_online: bool = True
    is_enabled: bool = True


class ProxyRead(MisModel):
    id: int
    last_known_ip: str = None
    # object_id: str


class ProxyReadSingle(MisModel):
    address: str
    change_url: str | None


class ProxyCreate(ProxyBase):
    # object_id: str
    address: str
    change_url: str | None


class ProxyUpdate(ProxyBase):
    address: str
    change_url: str | None


class ProxyCreateOutside(ProxyBase):
    pass


class ProxyCheckURL(MisModel):
    proxy_address: str | None
    id: int | None


class ProxyCheck(MisModel):
    status: int
    text: str
    exceptions: list
