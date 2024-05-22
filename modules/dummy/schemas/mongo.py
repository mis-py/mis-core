from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, Field, ConfigDict

PyObjectId = Annotated[str, BeforeValidator(str)]


class DummyItemCreate(BaseModel):
    name: str

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class DummyItemUpdate(BaseModel):
    name: Optional[str] = None


class DummyItemRead(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )