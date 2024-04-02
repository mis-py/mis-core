from typing import Optional

from pydantic import BaseModel


class RoutingKeyUpdate(BaseModel):
    key_verbose: str
    template: str


class RoutingKeyResponse(BaseModel):
    id: Optional[int]
    key: str
    name: str
    app_id: int
    key_verbose: Optional[str]
    template: Optional[str]
