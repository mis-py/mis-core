# from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel
from modules.binom_companion.db.models import LeadRecord

# Tortoise.init_models(["modules.binom_companion.db.models"], 'binom_companion')

LeadRecordModel = pydantic_model_creator(LeadRecord, name='LeadRecordModel')


class LeadRecordIn(PydanticModel):
    name: str
    last: str
    email: str
    ip: str
    ua: str
    country: str
    us: str
    uc: str
    un: str
    ut: str
    um: str
    phone: str
    subid: str
    sub2: str
    comment: str
    flow_id: int
    offer_name: str
    offer_index: str
    offer_id: int
    landing: str
    old_email: str
    aflw: str
    referer: str
    cookie: str
    time: int
    origin: str
    status: bool
    data: dict
