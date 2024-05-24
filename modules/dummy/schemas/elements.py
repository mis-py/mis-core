from typing import Optional

from pydantic import Field

from core.utils.schema import MisModel


class DummyElementRead(MisModel):
    id: int
    name: str
    is_visible: bool


class DummyElementUpdate(MisModel):
    id: int = Field(ge=1)
    name: Optional[str] = None
    is_visible: Optional[bool] = None
