from typing import Optional

from pydantic import BaseModel, ConfigDict

from core.schemas.common import UserModelShort, TeamModelShort


class DummyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dummy_string: str


class DummyCreate(BaseModel):
    dummy_string: str


class DummyEdit(BaseModel):
    dummy_string: str


class DummyRestrictedResponse(BaseModel):
    dummy_int: int


class DummyDataResponse(BaseModel):
    current_user: UserModelShort
    current_team: Optional[TeamModelShort]
    test_data: list[DummyResponse]
    variable: str
    module: str
    routing_keys: list[str]
