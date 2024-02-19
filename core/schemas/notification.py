from typing import Optional

from tortoise.contrib.pydantic import PydanticModel

from core.db.models import RoutingKey, RoutingKeySubscription
from pydantic import BaseModel


class EditRoutingKey(BaseModel):
    key_verbose: str
    template: str


class RoutingKeyModel(PydanticModel):
    id: Optional[int]
    key: str
    name: str
    app_id: int
    key_verbose: Optional[str]
    template: Optional[str]
    is_subscribed: bool = False

    class Config:
        orig_model = RoutingKey


class RoutingKeySubscriptionModel(PydanticModel):
    id: int
    routing_key: RoutingKeyModel

    class Config:
        orig_model = RoutingKeySubscription
