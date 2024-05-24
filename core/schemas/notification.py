from typing import Optional

from pydantic import BaseModel

from core.utils.schema import MisModel


class RoutingKeyUpdate(BaseModel):
    key_verbose: str
    template: str


class RoutingKeyResponse(MisModel):
    id: Optional[int]
    key: str
    name: str
    app_id: int
    key_verbose: Optional[str]
    template: Optional[str]


class RoutingKeySubscriptionResponse(MisModel):
    id: int
    user_id: int
    routing_key_id: int
