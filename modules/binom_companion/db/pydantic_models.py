from pydantic import BaseModel


class Lead(BaseModel):
    id: str = None

    name: str = None
    last: str = None

    ip: str = None
    ua: str = None
    country: str = None
    us: str = None
    uc: str = None
    un: str = None
    ut: str = None
    um: str = None
    subid: str = None
    flow_id: str = None
    offer_id: str = None
    landing: str = None
    aflw: str = None
    referer: str = None
    origin: str = None
    time: str = None
    status: str = None
    pin: str = None
    alter_id: str = None


