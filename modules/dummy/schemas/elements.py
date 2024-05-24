from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class DummyElementRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class DummyElementUpdate(BaseModel):
    id: int = Field(ge=1)
    name: Optional[str] = None

