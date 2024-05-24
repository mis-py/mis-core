from pydantic import BaseModel, ConfigDict

from modules.dummy.schemas.elements import DummyElementRead


class DummyCategoryRead(BaseModel):
    id: int
    name: str
    elements: list[DummyElementRead]


class DummyGroupRead(BaseModel):
    id: int
    name: str
    categories: list[DummyCategoryRead]

